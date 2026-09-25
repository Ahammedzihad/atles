import struct


VECTOR_DIMENSIONS = 768


def serialize_embedding(
    embedding: list[float],
) -> bytes:
    """Serialize a 768-dimensional embedding into SQLite BLOB bytes."""

    if not embedding:
        raise ValueError(
            "Embedding must not be empty."
        )

    if len(embedding) != VECTOR_DIMENSIONS:
        raise ValueError(
            f"Embedding must contain exactly "
            f"{VECTOR_DIMENSIONS} dimensions."
        )

    try:
        values = [
            float(value)
            for value in embedding
        ]
    except (TypeError, ValueError) as err:
        raise ValueError(
            "Embedding must contain only numeric values."
        ) from err

    return struct.pack(
        f"<{VECTOR_DIMENSIONS}f",
        *values,
    )


def deserialize_embedding(
    data: bytes | bytearray | memoryview,
) -> list[float]:
    """Deserialize SQLite BLOB bytes into an embedding vector."""

    if not data:
        raise ValueError(
            "Embedding data must not be empty."
        )

    expected_size = (
        VECTOR_DIMENSIONS * 4
    )

    if len(data) != expected_size:
        raise ValueError(
            f"Embedding data must contain exactly "
            f"{expected_size} bytes."
        )

    return list(
        struct.unpack(
            f"<{VECTOR_DIMENSIONS}f",
            bytes(data),
        )
    )