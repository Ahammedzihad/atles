import asyncio

import pytest

from app.memory.embeddings import EmbeddingService


def test_embedding_service_generates_vector():
    service = EmbeddingService()

    vector = asyncio.run(
        service.embed(
            "Atles is my personal AI assistant."
        )
    )

    assert isinstance(vector, list)
    assert len(vector) == 768
    assert all(
        isinstance(value, float)
        for value in vector
    )


def test_embedding_service_rejects_empty_text():
    service = EmbeddingService()

    with pytest.raises(ValueError):
        asyncio.run(
            service.embed("")
        )


def test_embedding_service_rejects_whitespace_text():
    service = EmbeddingService()

    with pytest.raises(ValueError):
        asyncio.run(
            service.embed("   ")
        )


def test_embedding_service_uses_configured_model():
    service = EmbeddingService(
        model="test-model"
    )

    assert service.model == "test-model"


def test_embedding_service_strips_base_url():
    service = EmbeddingService(
        base_url="http://127.0.0.1:11434/"
    )

    assert (
        service.base_url
        == "http://127.0.0.1:11434"
    )