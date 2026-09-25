from typing import Optional

from pydantic import BaseModel, Field


class MemoryCreate(BaseModel):
    memory_type: str = Field(
        ...,
        min_length=1,
        description=(
            "Type of memory, such as user, preference, "
            "project, or fact."
        ),
    )

    content: str = Field(
        ...,
        min_length=1,
        description="The information Atles should remember.",
    )

    importance: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Memory importance from 1 to 10.",
    )

    source: str = Field(
        default="manual",
        min_length=1,
        description="Source of the memory.",
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence that the memory is correct.",
    )

    tags: str = Field(
        default="",
        description="Comma-separated tags for the memory.",
    )


class MemoryUpdate(BaseModel):
    memory_type: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated memory type.",
    )

    content: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated memory content.",
    )

    importance: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Updated memory importance.",
    )

    source: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Updated memory source.",
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Updated memory confidence.",
    )

    tags: Optional[str] = Field(
        default=None,
        description="Updated comma-separated memory tags.",
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="Whether the memory is active.",
    )


class MemoryMerge(BaseModel):
    primary_memory_id: int = Field(
        ...,
        ge=1,
        description="ID of the memory that should survive the merge.",
    )

    secondary_memory_id: int = Field(
        ...,
        ge=1,
        description="ID of the memory that should be deactivated.",
    )

    merged_content: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Optional final content for the surviving memory.",
    )

    importance: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Optional new importance for the surviving memory.",
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional new confidence for the surviving memory.",
    )

    source: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Optional new source for the surviving memory.",
    )

    tags: Optional[str] = Field(
        default=None,
        description="Optional new comma-separated tags.",
    )


class MemoryCorrection(BaseModel):
    corrected_content: str = Field(
        ...,
        min_length=1,
        description="Corrected information that should replace the memory.",
    )

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional updated confidence.",
    )

    source: Optional[str] = Field(
        default=None,
        min_length=1,
        description="Optional updated source.",
    )

    tags: Optional[str] = Field(
        default=None,
        description="Optional updated comma-separated tags.",
    )


class MemoryResponse(BaseModel):
    id: int
    memory_type: str
    content: str
    importance: int
    created_at: str
    updated_at: str
    source: str
    confidence: float
    tags: str
    access_count: int
    last_used_at: Optional[str] = None
    is_active: bool


class MemoryListResponse(BaseModel):
    memories: list[MemoryResponse]


class MemorySearchResponse(BaseModel):
    memories: list[MemoryResponse]
    query: Optional[str] = None