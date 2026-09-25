from typing import Any


def fuse_memory_results(
    keyword_results: list[dict[str, Any]],
    semantic_results: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Combine keyword and semantic memory retrieval results.

    Memories appearing in both result sets are merged into one
    result instead of being returned twice.
    """

    if limit <= 0:
        return []

    memories: dict[int, dict[str, Any]] = {}

    for memory in keyword_results:
        memory_id = memory.get("id")

        if memory_id is None:
            continue

        result = dict(memory)

        result["keyword_score"] = float(
            memory.get("score", 0)
        )

        result["similarity"] = float(
            memory.get("similarity", 0.0)
        )

        result["retrieval_sources"] = {
            "keyword"
        }

        memories[memory_id] = result

    for memory in semantic_results:
        memory_id = memory.get("id")

        if memory_id is None:
            continue

        if memory_id in memories:
            result = memories[memory_id]

            result["similarity"] = float(
                memory.get("similarity", 0.0)
            )

            result["retrieval_sources"].add(
                "semantic"
            )

        else:
            result = dict(memory)

            result["keyword_score"] = float(
                memory.get("score", 0)
            )

            result["similarity"] = float(
                memory.get("similarity", 0.0)
            )

            result["retrieval_sources"] = {
                "semantic"
            }

            memories[memory_id] = result

    if not memories:
        return []

    for memory in memories.values():
        keyword_score = float(
            memory.get("keyword_score", 0.0)
        )

        similarity = float(
            memory.get("similarity", 0.0)
        )

        importance = float(
            memory.get("importance", 1)
        )

        confidence = float(
            memory.get("confidence", 1.0)
        )

        source_count = len(
            memory.get(
                "retrieval_sources",
                set(),
            )
        )

        memory["fusion_score"] = (
            keyword_score
            + (similarity * 100)
            + importance
            + (confidence * 2)
            + source_count
        )

    fused_results = list(
        memories.values()
    )

    fused_results.sort(
        key=lambda memory: (
            memory["fusion_score"],
            memory.get("importance", 1),
            memory.get("confidence", 1.0),
            memory.get("id", 0),
        ),
        reverse=True,
    )

    return fused_results[:limit]