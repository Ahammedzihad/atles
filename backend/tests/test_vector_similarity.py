import pytest

from app.memory.vector_similarity import cosine_similarity


def test_identical_vectors_have_similarity_one():
    first = [1.0, 2.0, 3.0]
    second = [1.0, 2.0, 3.0]

    result = cosine_similarity(
        first,
        second,
    )

    assert result == pytest.approx(1.0)


def test_opposite_vectors_have_similarity_negative_one():
    first = [1.0, 2.0, 3.0]
    second = [-1.0, -2.0, -3.0]

    result = cosine_similarity(
        first,
        second,
    )

    assert result == pytest.approx(-1.0)


def test_orthogonal_vectors_have_similarity_zero():
    first = [1.0, 0.0]
    second = [0.0, 1.0]

    result = cosine_similarity(
        first,
        second,
    )

    assert result == pytest.approx(0.0)


def test_similarity_is_symmetric():
    first = [1.0, 2.0, 3.0]
    second = [4.0, 5.0, 6.0]

    first_result = cosine_similarity(
        first,
        second,
    )

    second_result = cosine_similarity(
        second,
        first,
    )

    assert first_result == pytest.approx(
        second_result
    )


def test_different_dimensions_are_rejected():
    first = [1.0, 2.0]
    second = [1.0, 2.0, 3.0]

    with pytest.raises(ValueError):
        cosine_similarity(
            first,
            second,
        )


def test_empty_vectors_are_rejected():
    with pytest.raises(ValueError):
        cosine_similarity(
            [],
            [],
        )


def test_zero_vector_is_rejected():
    first = [0.0, 0.0, 0.0]
    second = [1.0, 2.0, 3.0]

    with pytest.raises(ValueError):
        cosine_similarity(
            first,
            second,
        )


def test_similarity_is_within_valid_cosine_range():
    first = [0.5, 1.5, -2.0]
    second = [2.0, -1.0, 0.5]

    result = cosine_similarity(
        first,
        second,
    )

    assert -1.0 <= result <= 1.0