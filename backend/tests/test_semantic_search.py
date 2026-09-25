import pytest

from app.memory.database import get_connection
from app.memory.models import create_tables
from app.memory.semantic_search import semantic_search_memories


@pytest.fixture(autouse=True)
def setup_database():
    create_tables()

    connection = get_connection()

    try:
        connection.execute(
            "DELETE FROM memories"
        )
        connection.commit()

    finally:
        connection.close()


def test_semantic_search_returns_similar_memory():
    from app.memory.service import save_memory

    save_memory(
        memory_type="preference",
        content="I prefer dark mode for my applications.",
        importance=5,
    )

    save_memory(
        memory_type="preference",
        content="I enjoy eating pizza on weekends.",
        importance=1,
    )

    results = semantic_search_memories(
        query="What interface theme do I like?",
        limit=2,
    )

    assert results
    assert results[0]["content"] == (
        "I prefer dark mode for my applications."
    )


def test_semantic_search_respects_limit():
    from app.memory.service import save_memory

    save_memory(
        memory_type="project",
        content="Atles is a personal AI assistant.",
    )

    save_memory(
        memory_type="project",
        content="Atles uses Python for its backend.",
    )

    save_memory(
        memory_type="project",
        content="Atles uses SQLite for memory storage.",
    )

    results = semantic_search_memories(
        query="Tell me about Atles.",
        limit=2,
    )

    assert len(results) <= 2


def test_semantic_search_rejects_empty_query():
    results = semantic_search_memories(
        query=""
    )

    assert results == []


def test_semantic_search_rejects_whitespace_query():
    results = semantic_search_memories(
        query="   "
    )

    assert results == []


def test_semantic_search_respects_min_similarity():
    from app.memory.service import save_memory

    save_memory(
        memory_type="test",
        content="Atles is a personal AI assistant.",
    )

    results = semantic_search_memories(
        query="Something completely unrelated.",
        limit=5,
        min_similarity=1.1,
    )

    assert results == []


def test_semantic_search_only_returns_active_memories():
    from app.memory.service import save_memory

    memory_id = save_memory(
        memory_type="project",
        content="Atles is my personal AI project.",
    )

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE memories
            SET is_active = 0
            WHERE id = ?
            """,
            (memory_id,),
        )
        connection.commit()

    finally:
        connection.close()

    results = semantic_search_memories(
        query="Tell me about my AI project.",
        limit=5,
    )

    assert all(
        memory["id"] != memory_id
        for memory in results
    )