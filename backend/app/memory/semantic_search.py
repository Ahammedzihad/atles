from typing import Optional

from app.memory.database import get_connection
from app.memory.embeddings import embedding_service
from app.memory.vector_similarity import cosine_similarity
from app.memory.vector_storage import deserialize_embedding


def semantic_search_memories(
    query: str,
    limit: int = 5,
    min_similarity: float = 0.0,
) -> list[dict]:
    """
    Search active memories using semantic similarity.

    The query is converted into an embedding and compared
    against stored memory embeddings using cosine similarity.
    """

    if not query or not query.strip():
        return []

    if limit <= 0:
        return []

    query_embedding = embedding_service.embed_sync(
        query
    )

    connection = get_connection()

    try:
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
              AND embedding IS NOT NULL
            """
        ).fetchall()

    finally:
        connection.close()

    scored_memories = []

    for row in rows:
        memory = dict(row)

        embedding_data = memory.get(
            "embedding"
        )

        if not embedding_data:
            continue

        try:
            memory_embedding = (
                deserialize_embedding(
                    embedding_data
                )
            )

            similarity = cosine_similarity(
                query_embedding,
                memory_embedding,
            )

        except (ValueError, TypeError):
            continue

        if similarity < min_similarity:
            continue

        memory["similarity"] = similarity

        scored_memories.append(
            memory
        )

    scored_memories.sort(
        key=lambda memory: (
            memory["similarity"],
            memory["importance"],
            memory["confidence"],
            memory["id"],
        ),
        reverse=True,
    )

    return scored_memories[:limit]


def get_semantic_memory_context(
    query: Optional[str] = None,
    limit: int = 5,
    min_similarity: float = 0.0,
) -> str:
    """
    Build a text context from semantically relevant memories.
    """

    if query is None:
        return ""

    memories = semantic_search_memories(
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