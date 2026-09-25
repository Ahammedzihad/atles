import sqlite3

from app.memory.database import get_connection
from app.memory.service import (
    correct_memory,
    create_conversation,
    conversation_exists,
    get_conversation_context,
    get_conversation_messages,
    get_memories,
    get_memory_context,
    get_semantic_memory_context,
    mark_memory_used,
    merge_memories,
    save_memory,
    save_message,
    search_memories,
    search_memories_semantically,
    update_memory,
)


def test_create_conversation():
    conversation_id = create_conversation(
        title="Test Conversation"
    )

    assert conversation_id > 0
    assert conversation_exists(conversation_id)


def test_conversation_exists_returns_false_for_unknown_id():
    assert conversation_exists(999999) is False


def test_save_and_get_conversation_messages():
    conversation_id = create_conversation(
        title="Message Test"
    )

    user_message_id = save_message(
        conversation_id=conversation_id,
        role="user",
        content="Hello Atles",
    )

    assistant_message_id = save_message(
        conversation_id=conversation_id,
        role="assistant",
        content="Hello! How can I help?",
    )

    assert user_message_id > 0
    assert assistant_message_id > 0

    messages = get_conversation_messages(
        conversation_id
    )

    assert len(messages) >= 2
    assert messages[-2]["role"] == "user"
    assert messages[-2]["content"] == "Hello Atles"
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"] == (
        "Hello! How can I help?"
    )


def test_get_conversation_context_respects_limit():
    conversation_id = create_conversation(
        title="Context Test"
    )

    for index in range(5):
        save_message(
            conversation_id=conversation_id,
            role="user",
            content=f"Message {index}",
        )

    context = get_conversation_context(
        conversation_id=conversation_id,
        limit=2,
    )

    assert len(context) == 2
    assert context[0]["content"] == "Message 3"
    assert context[1]["content"] == "Message 4"


def test_get_conversation_context_returns_empty_for_invalid_limit():
    conversation_id = create_conversation(
        title="Invalid Limit Test"
    )

    save_message(
        conversation_id=conversation_id,
        role="user",
        content="Test",
    )

    assert (
        get_conversation_context(
            conversation_id=conversation_id,
            limit=0,
        )
        == []
    )


def test_save_memory():
    memory_id = save_memory(
        memory_type="preference",
        content="User prefers concise answers.",
        importance=8,
        source="manual",
        confidence=0.95,
        tags="preference,communication",
    )

    assert memory_id > 0

    memories = get_memories()

    matching = [
        memory
        for memory in memories
        if memory["id"] == memory_id
    ]

    assert len(matching) == 1

    memory = matching[0]

    assert memory["memory_type"] == "preference"
    assert memory["content"] == (
        "User prefers concise answers."
    )
    assert memory["importance"] == 8
    assert memory["source"] == "manual"
    assert memory["confidence"] == 0.95
    assert memory["tags"] == (
        "preference,communication"
    )
    assert memory["is_active"] == 1


def test_get_memories_filters_inactive_memories():
    active_memory_id = save_memory(
        memory_type="fact",
        content="Active memory",
    )

    inactive_memory_id = save_memory(
        memory_type="fact",
        content="Inactive memory",
    )

    changed = update_memory(
        memory_id=inactive_memory_id,
        is_active=False,
    )

    assert changed is True

    active_memories = get_memories()

    active_ids = {
        memory["id"]
        for memory in active_memories
    }

    assert active_memory_id in active_ids
    assert inactive_memory_id not in active_ids

    all_memories = get_memories(
        active_only=False
    )

    all_ids = {
        memory["id"]
        for memory in all_memories
    }

    assert active_memory_id in all_ids
    assert inactive_memory_id in all_ids


def test_update_memory():
    memory_id = save_memory(
        memory_type="fact",
        content="Original content",
        importance=3,
        source="manual",
        confidence=0.5,
        tags="old",
    )

    changed = update_memory(
        memory_id=memory_id,
        memory_type="project",
        content="Updated content",
        importance=9,
        source="test",
        confidence=0.9,
        tags="updated,test",
    )

    assert changed is True

    memories = get_memories()

    memory = next(
        memory
        for memory in memories
        if memory["id"] == memory_id
    )

    assert memory["memory_type"] == "project"
    assert memory["content"] == "Updated content"
    assert memory["importance"] == 9
    assert memory["source"] == "test"
    assert memory["confidence"] == 0.9
    assert memory["tags"] == "updated,test"


def test_update_memory_returns_false_without_fields():
    memory_id = save_memory(
        memory_type="fact",
        content="Test content",
    )

    changed = update_memory(
        memory_id=memory_id,
    )

    assert changed is False


def test_update_memory_returns_false_for_unknown_id():
    changed = update_memory(
        memory_id=999999,
        content="Does not exist",
    )

    assert changed is False


def test_search_memories_finds_relevant_memory():
    memory_id = save_memory(
        memory_type="preference",
        content=(
            "User prefers concise technical explanations."
        ),
        importance=8,
        confidence=0.9,
        tags="communication,technical",
    )

    results = search_memories(
        query="technical explanations",
        limit=5,
    )

    result_ids = {
        memory["id"]
        for memory in results
    }

    assert memory_id in result_ids


def test_search_memories_ignores_inactive_memory():
    memory_id = save_memory(
        memory_type="fact",
        content="The user likes Python programming.",
    )

    update_memory(
        memory_id=memory_id,
        is_active=False,
    )

    results = search_memories(
        query="Python programming",
        limit=5,
    )

    result_ids = {
        memory["id"]
        for memory in results
    }

    assert memory_id not in result_ids


def test_search_memories_returns_empty_for_blank_query():
    assert search_memories(
        query="   ",
        limit=5,
    ) == []


def test_search_memories_returns_empty_for_invalid_limit():
    assert search_memories(
        query="Python",
        limit=0,
    ) == []


def test_search_memories_tracks_usage():
    memory_id = save_memory(
        memory_type="fact",
        content="Atles uses Python.",
    )

    before = get_memories()

    before_memory = next(
        memory
        for memory in before
        if memory["id"] == memory_id
    )

    assert before_memory["access_count"] == 0
    assert before_memory["last_used_at"] is None

    mark_memory_used(memory_id)

    after = get_memories()

    after_memory = next(
        memory
        for memory in after
        if memory["id"] == memory_id
    )

    assert after_memory["access_count"] == 1
    assert after_memory["last_used_at"] is not None


def test_get_memory_context_without_query():
    memory_id = save_memory(
        memory_type="project",
        content="Atles is a personal AI project.",
        importance=10,
    )

    context = get_memory_context()

    assert "Atles is a personal AI project." in context
    assert str(memory_id) not in context


def test_get_memory_context_with_query():
    save_memory(
        memory_type="project",
        content="Atles uses FastAPI.",
        importance=10,
    )

    context = get_memory_context(
        query="FastAPI",
        limit=5,
    )

    assert "Atles uses FastAPI." in context


def test_get_memory_context_returns_empty_when_no_memory_matches():
    context = get_memory_context(
        query="completely unrelated xyz123",
        limit=5,
    )

    assert context == ""


def test_search_memories_semantically():
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

    results = search_memories_semantically(
        query="What interface theme do I prefer?",
        limit=2,
    )

    assert results

    assert results[0]["content"] == (
        "I prefer dark mode for my applications."
    )

    assert "similarity" in results[0]


def test_search_memories_semantically_respects_limit():
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

    results = search_memories_semantically(
        query="Tell me about Atles.",
        limit=2,
    )

    assert len(results) <= 2


def test_get_semantic_memory_context():
    save_memory(
        memory_type="preference",
        content="I prefer dark mode for my applications.",
    )

    context = get_semantic_memory_context(
        query="What interface theme do I like?",
        limit=1,
    )

    assert context

    assert (
        "I prefer dark mode for my applications."
        in context
    )


def test_get_semantic_memory_context_without_query():
    context = get_semantic_memory_context()

    assert context == ""


def test_merge_memories():
    primary_id = save_memory(
        memory_type="project",
        content="Atles uses FastAPI.",
        importance=7,
        source="manual",
        confidence=0.8,
        tags="atles,backend",
    )

    secondary_id = save_memory(
        memory_type="project",
        content="The Atles backend is built with FastAPI.",
        importance=5,
        source="conversation",
        confidence=0.7,
        tags="backend,fastapi",
    )

    merged = merge_memories(
        primary_memory_id=primary_id,
        secondary_memory_id=secondary_id,
        merged_content=(
            "Atles backend uses FastAPI."
        ),
        importance=9,
        confidence=0.95,
        source="merged",
        tags="atles,backend,fastapi",
    )

    assert merged is True

    memories = get_memories(
        active_only=False
    )

    primary = next(
        memory
        for memory in memories
        if memory["id"] == primary_id
    )

    secondary = next(
        memory
        for memory in memories
        if memory["id"] == secondary_id
    )

    assert primary["content"] == (
        "Atles backend uses FastAPI."
    )
    assert primary["importance"] == 9
    assert primary["confidence"] == 0.95
    assert primary["source"] == "merged"
    assert primary["tags"] == (
        "atles,backend,fastapi"
    )
    assert primary["is_active"] == 1

    assert secondary["is_active"] == 0


def test_merge_memories_without_merged_content():
    primary_id = save_memory(
        memory_type="fact",
        content="Primary memory",
    )

    secondary_id = save_memory(
        memory_type="fact",
        content="Secondary memory",
    )

    merged = merge_memories(
        primary_memory_id=primary_id,
        secondary_memory_id=secondary_id,
    )

    assert merged is True

    memories = get_memories(
        active_only=False
    )

    primary = next(
        memory
        for memory in memories
        if memory["id"] == primary_id
    )

    secondary = next(
        memory
        for memory in memories
        if memory["id"] == secondary_id
    )

    assert primary["content"] == "Primary memory"
    assert secondary["is_active"] == 0


def test_merge_memories_rejects_same_memory():
    memory_id = save_memory(
        memory_type="fact",
        content="Same memory",
    )

    merged = merge_memories(
        primary_memory_id=memory_id,
        secondary_memory_id=memory_id,
    )

    assert merged is False


def test_merge_memories_rejects_unknown_primary():
    secondary_id = save_memory(
        memory_type="fact",
        content="Secondary",
    )

    merged = merge_memories(
        primary_memory_id=999999,
        secondary_memory_id=secondary_id,
    )

    assert merged is False


def test_merge_memories_rejects_unknown_secondary():
    primary_id = save_memory(
        memory_type="fact",
        content="Primary",
    )

    merged = merge_memories(
        primary_memory_id=primary_id,
        secondary_memory_id=999999,
    )

    assert merged is False


def test_merge_memories_rejects_inactive_primary():
    primary_id = save_memory(
        memory_type="fact",
        content="Primary",
    )

    secondary_id = save_memory(
        memory_type="fact",
        content="Secondary",
    )

    update_memory(
        memory_id=primary_id,
        is_active=False,
    )

    merged = merge_memories(
        primary_memory_id=primary_id,
        secondary_memory_id=secondary_id,
    )

    assert merged is False


def test_merge_memories_rejects_inactive_secondary():
    primary_id = save_memory(
        memory_type="fact",
        content="Primary",
    )

    secondary_id = save_memory(
        memory_type="fact",
        content="Secondary",
    )

    update_memory(
        memory_id=secondary_id,
        is_active=False,
    )

    merged = merge_memories(
        primary_memory_id=primary_id,
        secondary_memory_id=secondary_id,
    )

    assert merged is False


def test_merge_memories_rejects_blank_merged_content():
    primary_id = save_memory(
        memory_type="fact",
        content="Primary",
    )

    secondary_id = save_memory(
        memory_type="fact",
        content="Secondary",
    )

    merged = merge_memories(
        primary_memory_id=primary_id,
        secondary_memory_id=secondary_id,
        merged_content="   ",
    )

    assert merged is False

    memories = get_memories(
        active_only=False
    )

    primary = next(
        memory
        for memory in memories
        if memory["id"] == primary_id
    )

    secondary = next(
        memory
        for memory in memories
        if memory["id"] == secondary_id
    )

    assert primary["is_active"] == 1
    assert secondary["is_active"] == 1


def test_correct_memory():
    memory_id = save_memory(
        memory_type="fact",
        content="Atles uses an old model.",
        importance=6,
        source="old-source",
        confidence=0.5,
        tags="old",
    )

    corrected = correct_memory(
        memory_id=memory_id,
        corrected_content=(
            "Atles uses the current model."
        ),
        confidence=0.95,
        source="correction",
        tags="corrected,current",
    )

    assert corrected is True

    memories = get_memories()

    memory = next(
        memory
        for memory in memories
        if memory["id"] == memory_id
    )

    assert memory["content"] == (
        "Atles uses the current model."
    )
    assert memory["confidence"] == 0.95
    assert memory["source"] == "correction"
    assert memory["tags"] == "corrected,current"
    assert memory["is_active"] == 1


def test_correct_memory_keeps_same_id():
    memory_id = save_memory(
        memory_type="fact",
        content="Original fact",
    )

    corrected = correct_memory(
        memory_id=memory_id,
        corrected_content="Corrected fact",
    )

    assert corrected is True

    memories = get_memories()

    ids = {
        memory["id"]
        for memory in memories
    }

    assert memory_id in ids

    memory = next(
        memory
        for memory in memories
        if memory["id"] == memory_id
    )

    assert memory["content"] == "Corrected fact"


def test_correct_memory_rejects_blank_content():
    memory_id = save_memory(
        memory_type="fact",
        content="Original fact",
    )

    corrected = correct_memory(
        memory_id=memory_id,
        corrected_content="   ",
    )

    assert corrected is False

    memories = get_memories()

    memory = next(
        memory
        for memory in memories
        if memory["id"] == memory_id
    )

    assert memory["content"] == "Original fact"


def test_correct_memory_rejects_unknown_memory():
    corrected = correct_memory(
        memory_id=999999,
        corrected_content="Corrected fact",
    )

    assert corrected is False


def test_correct_memory_rejects_inactive_memory():
    memory_id = save_memory(
        memory_type="fact",
        content="Inactive fact",
    )

    update_memory(
        memory_id=memory_id,
        is_active=False,
    )

    corrected = correct_memory(
        memory_id=memory_id,
        corrected_content="Corrected fact",
    )

    assert corrected is False

    memories = get_memories(
        active_only=False
    )

    memory = next(
        memory
        for memory in memories
        if memory["id"] == memory_id
    )

    assert memory["content"] == "Inactive fact"
    assert memory["is_active"] == 0


def test_correct_memory_preserves_existing_optional_fields():
    memory_id = save_memory(
        memory_type="fact",
        content="Original fact",
        confidence=0.7,
        source="original",
        tags="original",
    )

    corrected = correct_memory(
        memory_id=memory_id,
        corrected_content="Corrected fact",
    )

    assert corrected is True

    memories = get_memories()

    memory = next(
        memory
        for memory in memories
        if memory["id"] == memory_id
    )

    assert memory["content"] == "Corrected fact"
    assert memory["confidence"] == 0.7
    assert memory["source"] == "original"
    assert memory["tags"] == "original"


def test_database_connection_uses_sqlite():
    connection = get_connection()

    try:
        assert isinstance(
            connection,
            sqlite3.Connection,
        )
    finally:
        connection.close()