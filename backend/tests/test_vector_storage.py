import pytest

from app.memory.vector_storage import (
    VECTOR_DIMENSIONS,
    deserialize_embedding,
    serialize_embedding,
)


def test_serialize_embedding():
    embedding = [
        float(index)
        for index in range(VECTOR_DIMENSIONS)
    ]

    data = serialize_embedding(embedding)

    assert isinstance(data, bytes)
    assert len(data) == VECTOR_DIMENSIONS * 4


def test_deserialize_embedding():
    embedding = [
        float(index)
        for index in range(VECTOR_DIMENSIONS)
    ]

    data = serialize_embedding(embedding)
    restored = deserialize_embedding(data)

    assert isinstance(restored, list)
    assert len(restored) == VECTOR_DIMENSIONS

    for original, restored_value in zip(
        embedding,
        restored,
    ):
        assert restored_value == pytest.approx(
            original,
            rel=1e-6,
        )


def test_round_trip_preserves_embedding():
    embedding = [
        0.125,
        -0.5,
        1.25,
        -2.75,
    ] * 192

    assert len(embedding) == VECTOR_DIMENSIONS

    data = serialize_embedding(embedding)
    restored = deserialize_embedding(data)

    assert restored == pytest.approx(
        embedding,
        rel=1e-6,
    )


def test_serialize_rejects_empty_embedding():
    with pytest.raises(ValueError):
        serialize_embedding([])


def test_serialize_rejects_wrong_dimensions():
    embedding = [0.1] * 10

    with pytest.raises(ValueError):
        serialize_embedding(embedding)


def test_deserialize_rejects_empty_data():
    with pytest.raises(ValueError):
        deserialize_embedding(b"")


def test_deserialize_rejects_wrong_size():
    with pytest.raises(ValueError):
        deserialize_embedding(b"\x00" * 100)