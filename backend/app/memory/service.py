import re
from typing import Optional

from app.memory.database import get_connection
from app.memory.embeddings import embedding_service
from app.memory.semantic_search import (
    semantic_search_memories,
)
from app.memory.vector_storage import serialize_embedding


def create_conversation(
    title: Optional[str] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO conversations (title)
            VALUES (?)
            """,
            (title,),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def conversation_exists(
    conversation_id: int,
) -> bool:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        ).fetchone()

        return row is not None

    finally:
        connection.close()


def save_message(
    conversation_id: int,
    role: str,
    content: str,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content
            )
            VALUES (?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content,
            ),
        )

        connection.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_conversation_messages(
    conversation_id: int,
) -> list[dict]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                conversation_id,
                role,
                content,
                created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def save_memory(
    memory_type: str,
    content: str,
    importance: int = 1,
    source: str = "manual",
    confidence: float = 1.0,
    tags: str = "",
) -> int:
    """
    Save a memory and generate its semantic embedding.

    The embedding is generated before the database write so that
    a memory is not created without its vector representation.
    """

    if not content.strip():
        raise ValueError(
            "Memory content must not be empty."
        )

    embedding = embedding_service.embed_sync(
        content
    )

    embedding_blob = serialize_embedding(
        embedding
    )

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO memories (
                memory_type,
                content,
                importance,
                source,
                confidence,
                tags,
                embedding
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_type,
                content,
                importance,
                source,
                confidence,
                tags,
                embedding_blob,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def update_memory(
    memory_id: int,
    memory_type: Optional[str] = None,
    content: Optional[str] = None,
    importance: Optional[int] = None,
    source: Optional[str] = None,
    confidence: Optional[float] = None,
    tags: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> bool:
    updates = []
    values = []

    if memory_type is not None:
        updates.append("memory_type = ?")
        values.append(memory_type)

    if content is not None:
        updates.append("content = ?")
        values.append(content)

    if importance is not None:
        updates.append("importance = ?")
        values.append(importance)

    if source is not None:
        updates.append("source = ?")
        values.append(source)

    if confidence is not None:
        updates.append("confidence = ?")
        values.append(confidence)

    if tags is not None:
        updates.append("tags = ?")
        values.append(tags)

    if is_active is not None:
        updates.append("is_active = ?")
        values.append(
            1 if is_active else 0
        )

    if not updates:
        return False

    updates.append(
        "updated_at = CURRENT_TIMESTAMP"
    )

    values.append(memory_id)

    connection = get_connection()

    try:
        cursor = connection.execute(
            f"""
            UPDATE memories
            SET {", ".join(updates)}
            WHERE id = ?
            """,
            values,
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def merge_memories(
    primary_memory_id: int,
    secondary_memory_id: int,
    merged_content: Optional[str] = None,
    importance: Optional[int] = None,
    confidence: Optional[float] = None,
    source: Optional[str] = None,
    tags: Optional[str] = None,
) -> bool:
    """
    Merge two active memories.

    The primary memory survives.
    The secondary memory becomes inactive.
    """

    if primary_memory_id == secondary_memory_id:
        return False

    connection = get_connection()

    try:
        primary = connection.execute(
            """
            SELECT
                id,
                is_active
            FROM memories
            WHERE id = ?
            """,
            (primary_memory_id,),
        ).fetchone()

        secondary = connection.execute(
            """
            SELECT
                id,
                is_active
            FROM memories
            WHERE id = ?
            """,
            (secondary_memory_id,),
        ).fetchone()

        if primary is None or secondary is None:
            return False

        if not primary["is_active"]:
            return False

        if not secondary["is_active"]:
            return False

        updates = []
        values = []

        if merged_content is not None:
            if not merged_content.strip():
                return False

            updates.append("content = ?")
            values.append(
                merged_content.strip()
            )

        if importance is not None:
            updates.append("importance = ?")
            values.append(importance)

        if confidence is not None:
            updates.append("confidence = ?")
            values.append(confidence)

        if source is not None:
            updates.append("source = ?")
            values.append(source)

        if tags is not None:
            updates.append("tags = ?")
            values.append(tags)

        updates.append(
            "updated_at = CURRENT_TIMESTAMP"
        )

        values.append(primary_memory_id)

        connection.execute(
            f"""
            UPDATE memories
            SET {", ".join(updates)}
            WHERE id = ?
            """,
            values,
        )

        connection.execute(
            """
            UPDATE memories
            SET
                is_active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (secondary_memory_id,),
        )

        connection.commit()

        return True

    finally:
        connection.close()


def correct_memory(
    memory_id: int,
    corrected_content: str,
    confidence: Optional[float] = None,
    source: Optional[str] = None,
    tags: Optional[str] = None,
) -> bool:
    """
    Correct an active memory while keeping the same memory ID.
    """

    if not corrected_content.strip():
        return False

    connection = get_connection()

    try:
        existing = connection.execute(
            """
            SELECT
                id,
                is_active
            FROM memories
            WHERE id = ?
            """,
            (memory_id,),
        ).fetchone()

        if existing is None:
            return False

        if not existing["is_active"]:
            return False

        updates = [
            "content = ?",
            "updated_at = CURRENT_TIMESTAMP",
        ]

        values = [
            corrected_content.strip(),
        ]

        if confidence is not None:
            updates.append(
                "confidence = ?"
            )
            values.append(confidence)

        if source is not None:
            updates.append(
                "source = ?"
            )
            values.append(source)

        if tags is not None:
            updates.append(
                "tags = ?"
            )
            values.append(tags)

        values.append(memory_id)

        cursor = connection.execute(
            f"""
            UPDATE memories
            SET {", ".join(updates)}
            WHERE id = ?
            """,
            values,
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def get_memories(
    memory_type: Optional[str] = None,
    active_only: bool = True,
) -> list[dict]:
    connection = get_connection()

    try:
        if memory_type is None:
            if active_only:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        memory_type,
                        content,
                        importance,
                        created_at,
                        updated_at,
                        source,
                        confidence,
                        tags,
                        access_count,
                        last_used_at,
                        is_active,
                        embedding
                    FROM memories
                    WHERE is_active = 1
                    ORDER BY importance DESC, id DESC
                    """
                ).fetchall()

            else:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        memory_type,
                        content,
                        importance,
                        created_at,
                        updated_at,
                        source,
                        confidence,
                        tags,
                        access_count,
                        last_used_at,
                        is_active,
                        embedding
                    FROM memories
                    ORDER BY importance DESC, id DESC
                    """
                ).fetchall()

        else:
            if active_only:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        memory_type,
                        content,
                        importance,
                        created_at,
                        updated_at,
                        source,
                        confidence,
                        tags,
                        access_count,
                        last_used_at,
                        is_active,
                        embedding
                    FROM memories
                    WHERE memory_type = ?
                      AND is_active = 1
                    ORDER BY importance DESC, id DESC
                    """,
                    (memory_type,),
                ).fetchall()

            else:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        memory_type,
                        content,
                        importance,
                        created_at,
                        updated_at,
                        source,
                        confidence,
                        tags,
                        access_count,
                        last_used_at,
                        is_active,
                        embedding
                    FROM memories
                    WHERE memory_type = ?
                    ORDER BY importance DESC, id DESC
                    """,
                    (memory_type,),
                ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def _tokenize(
    text: str,
) -> set[str]:
    words = re.findall(
        r"\b[a-zA-Z0-9_]+\b",
        text.lower(),
    )

    stop_words = {
        "the",
        "and",
        "that",
        "this",
        "with",
        "from",
        "have",
        "your",
        "you",
        "are",
        "for",
        "was",
        "were",
        "what",
        "when",
        "where",
        "how",
        "why",
        "who",
        "can",
        "could",
        "would",
        "should",
        "will",
        "about",
        "into",
        "then",
        "than",
        "there",
        "their",
        "they",
        "them",
        "its",
        "it's",
    }

    return {
        word
        for word in words
        if len(word) >= 3
        and word not in stop_words
    }


def _memory_score(
    query_tokens: set[str],
    memory: dict,
) -> int:
    memory_text = (
        f"{memory['memory_type']} "
        f"{memory['content']} "
        f"{memory.get('tags', '')}"
    )

    memory_tokens = _tokenize(
        memory_text
    )

    overlap = query_tokens.intersection(
        memory_tokens
    )

    if not overlap:
        return 0

    importance = int(
        memory.get("importance", 1)
    )

    confidence = float(
        memory.get("confidence", 1.0)
    )

    confidence_bonus = round(
        confidence * 2
    )

    return (
        len(overlap) * 10
        + importance
        + confidence_bonus
    )


def search_memories(
    query: str,
    limit: int = 5,
) -> list[dict]:
    """
    Search memories using keyword matching.
    """

    if not query or not query.strip():
        return []

    if limit <= 0:
        return []

    query_tokens = _tokenize(
        query
    )

    if not query_tokens:
        return []

    memories = get_memories(
        active_only=True
    )

    scored_memories = []

    for memory in memories:
        score = _memory_score(
            query_tokens,
            memory,
        )

        if score > 0:
            memory_with_score = dict(
                memory
            )

            memory_with_score["score"] = (
                score
            )

            scored_memories.append(
                memory_with_score
            )

    scored_memories.sort(
        key=lambda memory: (
            memory["score"],
            memory["importance"],
            memory["confidence"],
            memory["id"],
        ),
        reverse=True,
    )

    selected_memories = (
        scored_memories[:limit]
    )

    for memory in selected_memories:
        mark_memory_used(
            memory["id"]
        )

    return selected_memories


def search_memories_semantically(
    query: str,
    limit: int = 5,
    min_similarity: float = 0.0,
) -> list[dict]:
    """
    Search memories using semantic similarity.
    """

    if not query or not query.strip():
        return []

    if limit <= 0:
        return []

    results = semantic_search_memories(
        query=query,
        limit=limit,
        min_similarity=min_similarity,
    )

    for memory in results:
        mark_memory_used(
            memory["id"]
        )

    return results


def search_memories_fused(
    query: str,
    limit: int = 5,
    min_similarity: float = 0.0,
) -> list[dict]:
    """
    Search memories using both keyword and semantic retrieval,
    then fuse the results into one ranked list.
    """

    if not query or not query.strip():
        return []

    if limit <= 0:
        return []

    from app.memory.fusion import (
        fuse_memory_results,
    )

    keyword_results = search_memories(
        query=query,
        limit=limit,
    )

    semantic_results = (
        search_memories_semantically(
            query=query,
            limit=limit,
            min_similarity=min_similarity,
        )
    )

    return fuse_memory_results(
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        limit=limit,
    )


def mark_memory_used(
    memory_id: int,
) -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE memories
            SET
                access_count = access_count + 1,
                last_used_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (memory_id,),
        )

        connection.commit()

    finally:
        connection.close()


def get_memory_context(
    query: Optional[str] = None,
    limit: int = 5,
) -> str:
    if query is None:
        memories = get_memories()

    else:
        memories = search_memories(
            query=query,
            limit=limit,
        )

    if not memories:
        return ""

    lines = []

    for memory in memories:
        lines.append(
            f"[{memory['memory_type']}] "
            f"{memory['content']}"
        )

    return "\n".join(lines)


def get_semantic_memory_context(
    query: Optional[str] = None,
    limit: int = 5,
    min_similarity: float = 0.0,
) -> str:
    """
    Build memory context using semantic retrieval.

    Semantic retrieval requires a query.
    """

    if query is None or not query.strip():
        return ""

    memories = search_memories_semantically(
        query=query,
        limit=limit,
        min_similarity=min_similarity,
    )

    if not memories:
        return ""

    lines = []

    for memory in memories:
        lines.append(
            f"[{memory['memory_type']}] "
            f"{memory['content']}"
        )

    return "\n".join(lines)


def get_fused_memory_context(
    query: Optional[str] = None,
    limit: int = 5,
    min_similarity: float = 0.0,
) -> str:
    """
    Build memory context using fused keyword
    and semantic retrieval.

    Fused retrieval requires a query.
    """

    if query is None or not query.strip():
        return ""

    memories = search_memories_fused(
        query=query,
        limit=limit,
        min_similarity=min_similarity,
    )

    if not memories:
        return ""

    lines = []

    for memory in memories:
        lines.append(
            f"[{memory['memory_type']}] "
            f"{memory['content']}"
        )

    return "\n".join(lines)


def get_conversation_context(
    conversation_id: int,
    limit: int = 20,
) -> list[dict]:
    """
    Return recent conversation messages in chronological order.

    The most recent messages are kept so the prompt does not
    grow without limit.
    """

    messages = get_conversation_messages(
        conversation_id
    )

    if limit <= 0:
        return []

    if len(messages) <= limit:
        return messages

    return messages[-limit:]