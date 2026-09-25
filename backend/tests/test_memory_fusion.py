
from unittest.mock import patch

from app.memory.database import get_connection
from app.memory.models import create_tables
from app.memory.service import (
    save_memory,
    search_memories_fused,
)
from app.memory.fusion import fuse_memory_results


def setup_function():
    create_tables()

    connection = get_connection()

    try:
        connection.execute(
            "DELETE FROM memories"
        )
        connection.commit()

    finally:
        connection.close()


def test_fusion_returns_keyword_only_memory():
    memory_id = save_memory(
        memory_type="project",
        content="Atles uses Python.",
        importance=5,
        confidence=0.9,
    )

    keyword_results = [
        {
            "id": memory_id,
            "memory_type": "project",
            "content": "Atles uses Python.",
            "importance": 5,
            "confidence": 0.9,
            "score": 25,
        }
    ]

    semantic_results = []

    results = fuse_memory_results(
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        limit=5,
    )

    assert len(results) == 1
    assert results[0]["id"] == memory_id


def test_fusion_returns_semantic_only_memory():
    memory_id = save_memory(
        memory_type="preference",
        content="I prefer dark mode.",
        importance=5,
        confidence=0.9,
    )

    keyword_results = []

    semantic_results = [
        {
            "id": memory_id,
            "memory_type": "preference",
            "content": "I prefer dark mode.",
            "importance": 5,
            "confidence": 0.9,
            "similarity": 0.85,
        }
    ]

    results = fuse_memory_results(
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        limit=5,
    )

    assert len(results) == 1
    assert results[0]["id"] == memory_id


def test_fusion_removes_duplicate_memory():
    memory_id = save_memory(
        memory_type="project",
        content="Atles uses FastAPI.",
        importance=8,
        confidence=0.95,
    )

    keyword_results = [
        {
            "id": memory_id,
            "memory_type": "project",
            "content": "Atles uses FastAPI.",
            "importance": 8,
            "confidence": 0.95,
            "score": 32,
        }
    ]

    semantic_results = [
        {
            "id": memory_id,
            "memory_type": "project",
            "content": "Atles uses FastAPI.",
            "importance": 8,
            "confidence": 0.95,
            "similarity": 0.92,
        }
    ]

    results = fuse_memory_results(
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        limit=5,
    )

    assert len(results) == 1
    assert results[0]["id"] == memory_id


def test_fusion_marks_duplicate_as_combined():
    memory_id = save_memory(
        memory_type="project",
        content="Atles uses FastAPI.",
        importance=8,
        confidence=0.95,
    )

    keyword_results = [
        {
            "id": memory_id,
            "memory_type": "project",
            "content": "Atles uses FastAPI.",
            "importance": 8,
            "confidence": 0.95,
            "score": 32,
        }
    ]

    semantic_results = [
        {
            "id": memory_id,
            "memory_type": "project",
            "content": "Atles uses FastAPI.",
            "importance": 8,
            "confidence": 0.95,
            "similarity": 0.92,
        }
    ]

    results = fuse_memory_results(
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        limit=5,
    )

    assert len(results) == 1

    result = results[0]

    assert result["id"] == memory_id
    assert result["keyword_score"] == 32
    assert result["similarity"] == 0.92
    assert result["retrieval_sources"] == {
        "keyword",
        "semantic",
    }


def test_fusion_respects_limit():
    memories = []

    for index in range(5):
        memory_id = save_memory(
            memory_type="project",
            content=f"Atles project fact {index}.",
        )

        memories.append(memory_id)

    keyword_results = [
        {
            "id": memory_id,
            "memory_type": "project",
            "content": f"Atles project fact {index}.",
            "importance": 1,
            "confidence": 1.0,
            "score": 10 - index,
        }
        for index, memory_id in enumerate(memories)
    ]

    results = fuse_memory_results(
        keyword_results=keyword_results,
        semantic_results=[],
        limit=3,
    )

    assert len(results) == 3


def test_fusion_empty_results():
    results = fuse_memory_results(
        keyword_results=[],
        semantic_results=[],
        limit=5,
    )

    assert results == []


def test_fusion_rejects_invalid_limit():
    results = fuse_memory_results(
        keyword_results=[],
        semantic_results=[],
        limit=0,
    )

    assert results == []


def test_fusion_combines_metadata_from_both_sources():
    memory_id = save_memory(
        memory_type="preference",
        content="I prefer concise answers.",
        importance=9,
        confidence=0.95,
        tags="communication",
    )

    keyword_results = [
        {
            "id": memory_id,
            "memory_type": "preference",
            "content": "I prefer concise answers.",
            "importance": 9,
            "confidence": 0.95,
            "tags": "communication",
            "score": 28,
        }
    ]

    semantic_results = [
        {
            "id": memory_id,
            "memory_type": "preference",
            "content": "I prefer concise answers.",
            "importance": 9,
            "confidence": 0.95,
            "tags": "communication",
            "similarity": 0.88,
        }
    ]

    results = fuse_memory_results(
        keyword_results=keyword_results,
        semantic_results=semantic_results,
        limit=5,
    )

    assert len(results) == 1

    result = results[0]

    assert result["memory_type"] == "preference"
    assert result["content"] == (
        "I prefer concise answers."
    )
    assert result["importance"] == 9
    assert result["confidence"] == 0.95
    assert result["tags"] == "communication"


def test_search_memories_fused_combines_keyword_and_semantic_results():
    first_memory_id = save_memory(
        memory_type="project",
        content="Atles uses FastAPI for its backend.",
        importance=8,
        confidence=0.95,
    )

    second_memory_id = save_memory(
        memory_type="project",
        content="Atles uses SQLite for memory storage.",
        importance=6,
        confidence=0.9,
    )

    keyword_results = [
        {
            "id": first_memory_id,
            "memory_type": "project",
            "content": "Atles uses FastAPI for its backend.",
            "importance": 8,
            "confidence": 0.95,
            "score": 22,
        }
    ]

    semantic_results = [
        {
            "id": first_memory_id,
            "memory_type": "project",
            "content": "Atles uses FastAPI for its backend.",
            "importance": 8,
            "confidence": 0.95,
            "similarity": 0.92,
        },
        {
            "id": second_memory_id,
            "memory_type": "project",
            "content": "Atles uses SQLite for memory storage.",
            "importance": 6,
            "confidence": 0.9,
            "similarity": 0.80,
        },
    ]

    with patch(
        "app.memory.service.search_memories",
        return_value=keyword_results,
    ), patch(
        "app.memory.service.search_memories_semantically",
        return_value=semantic_results,
    ):
        results = search_memories_fused(
            query="How does Atles store and run its backend?",
            limit=5,
        )

    result_ids = [
        memory["id"]
        for memory in results
    ]

    assert result_ids.count(
        first_memory_id
    ) == 1

    assert second_memory_id in result_ids

    assert len(results) == 2


def test_search_memories_fused_respects_limit():
    memories = []

    for index in range(5):
        memory_id = save_memory(
            memory_type="project",
            content=f"Atles project fact {index}.",
        )

        memories.append(memory_id)

    semantic_results = [
        {
            "id": memory_id,
            "memory_type": "project",
            "content": f"Atles project fact {index}.",
            "importance": 1,
            "confidence": 1.0,
            "similarity": 0.8 - (index * 0.05),
        }
        for index, memory_id in enumerate(memories)
    ]

    with patch(
        "app.memory.service.search_memories",
        return_value=[],
    ), patch(
        "app.memory.service.search_memories_semantically",
        return_value=semantic_results,
    ):
        results = search_memories_fused(
            query="Tell me about Atles.",
            limit=3,
        )

    assert len(results) == 3


def test_search_memories_fused_returns_empty_for_blank_query():
    results = search_memories_fused(
        query="   ",
        limit=5,
    )

    assert results == []


def test_search_memories_fused_returns_empty_for_invalid_limit():
    results = search_memories_fused(
        query="Atles",
        limit=0,
    )

    assert results == []
