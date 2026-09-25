from fastapi import APIRouter, HTTPException, Query, status

from app.memory.database import get_connection
from app.memory.service import (
    get_memories,
    merge_memories,
    correct_memory,
    save_memory,
    search_memories,
    update_memory,
)
from app.schemas.memory import (
    MemoryCorrection,
    MemoryCreate,
    MemoryListResponse,
    MemoryMerge,
    MemoryResponse,
    MemorySearchResponse,
    MemoryUpdate,
)

router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


def _get_memory_by_id(
    memory_id: int,
) -> dict | None:
    connection = get_connection()

    try:
        row = connection.execute(
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
                is_active
            FROM memories
            WHERE id = ?
            """,
            (memory_id,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a memory",
)
async def create_memory(
    payload: MemoryCreate,
) -> MemoryResponse:
    memory_id = save_memory(
        memory_type=payload.memory_type,
        content=payload.content,
        importance=payload.importance,
        source=payload.source,
        confidence=payload.confidence,
        tags=payload.tags,
    )

    memory = _get_memory_by_id(memory_id)

    if memory is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory was created but could not be retrieved.",
        )

    return MemoryResponse(**memory)


@router.get(
    "",
    response_model=MemoryListResponse,
    summary="List memories",
)
async def list_memories() -> MemoryListResponse:
    memories = get_memories()

    return MemoryListResponse(
        memories=[
            MemoryResponse(**memory)
            for memory in memories
        ]
    )


@router.get(
    "/search",
    response_model=MemorySearchResponse,
    summary="Search memories",
)
async def search_memory_endpoint(
    query: str = Query(
        ...,
        min_length=1,
        description="Search text for finding relevant memories.",
    ),
    limit: int = Query(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of memories to return.",
    ),
) -> MemorySearchResponse:
    memories = search_memories(
        query=query,
        limit=limit,
    )

    return MemorySearchResponse(
        memories=[
            MemoryResponse(**memory)
            for memory in memories
        ],
        query=query,
    )


@router.post(
    "/merge",
    response_model=MemoryResponse,
    summary="Merge two memories",
)
async def merge_memory_endpoint(
    payload: MemoryMerge,
) -> MemoryResponse:
    if payload.primary_memory_id == payload.secondary_memory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primary and secondary memory IDs must be different.",
        )

    primary_memory = _get_memory_by_id(
        payload.primary_memory_id
    )

    if primary_memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Memory {payload.primary_memory_id} "
                "not found."
            ),
        )

    secondary_memory = _get_memory_by_id(
        payload.secondary_memory_id
    )

    if secondary_memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Memory {payload.secondary_memory_id} "
                "not found."
            ),
        )

    if not primary_memory["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Primary memory {payload.primary_memory_id} "
                "is inactive."
            ),
        )

    if not secondary_memory["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Secondary memory {payload.secondary_memory_id} "
                "is inactive."
            ),
        )

    merged = merge_memories(
        primary_memory_id=payload.primary_memory_id,
        secondary_memory_id=payload.secondary_memory_id,
        merged_content=payload.merged_content,
        importance=payload.importance,
        confidence=payload.confidence,
        source=payload.source,
        tags=payload.tags,
    )

    if not merged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Memories could not be merged.",
        )

    updated_memory = _get_memory_by_id(
        payload.primary_memory_id
    )

    if updated_memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Primary memory {payload.primary_memory_id} "
                "could not be retrieved after merge."
            ),
        )

    return MemoryResponse(**updated_memory)


@router.post(
    "/{memory_id}/correct",
    response_model=MemoryResponse,
    summary="Correct a memory",
)
async def correct_memory_endpoint(
    memory_id: int,
    payload: MemoryCorrection,
) -> MemoryResponse:
    memory = _get_memory_by_id(memory_id)

    if memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found.",
        )

    if not memory["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Memory {memory_id} is inactive.",
        )

    corrected = correct_memory(
        memory_id=memory_id,
        corrected_content=payload.corrected_content,
        confidence=payload.confidence,
        source=payload.source,
        tags=payload.tags,
    )

    if not corrected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Memory could not be corrected.",
        )

    updated_memory = _get_memory_by_id(memory_id)

    if updated_memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Memory {memory_id} "
                "could not be retrieved after correction."
            ),
        )

    return MemoryResponse(**updated_memory)


@router.get(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="Get a memory",
)
async def get_memory(
    memory_id: int,
) -> MemoryResponse:
    memory = _get_memory_by_id(memory_id)

    if memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found.",
        )

    return MemoryResponse(**memory)


@router.put(
    "/{memory_id}",
    response_model=MemoryResponse,
    summary="Update a memory",
)
async def update_memory_endpoint(
    memory_id: int,
    payload: MemoryUpdate,
) -> MemoryResponse:
    memory_exists = _get_memory_by_id(memory_id)

    if memory_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found.",
        )

    changed = update_memory(
        memory_id=memory_id,
        memory_type=payload.memory_type,
        content=payload.content,
        importance=payload.importance,
        source=payload.source,
        confidence=payload.confidence,
        tags=payload.tags,
        is_active=payload.is_active,
    )

    if not changed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No memory fields were provided for update.",
        )

    updated_memory = _get_memory_by_id(memory_id)

    if updated_memory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found.",
        )

    return MemoryResponse(**updated_memory)


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete a memory",
)
async def delete_memory(
    memory_id: int,
) -> None:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM memories
            WHERE id = ?
            """,
            (memory_id,),
        )

        connection.commit()

    finally:
        connection.close()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory {memory_id} not found.",
        )