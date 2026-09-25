import math


def cosine_similarity(
    first: list[float],
    second: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if not first or not second:
        raise ValueError(
            "Vectors must not be empty."
        )

    if len(first) != len(second):
        raise ValueError(
            "Vectors must have the same dimensions."
        )

    first_magnitude = math.sqrt(
        sum(value * value for value in first)
    )

    second_magnitude = math.sqrt(
        sum(value * value for value in second)
    )

    if first_magnitude == 0:
        raise ValueError(
            "The first vector must not be a zero vector."
        )

    if second_magnitude == 0:
        raise ValueError(
            "The second vector must not be a zero vector."
        )

    dot_product = sum(
        first_value * second_value
        for first_value, second_value in zip(
            first,
            second,
        )
    )

    return (
        dot_product
        / (first_magnitude * second_magnitude)
    )