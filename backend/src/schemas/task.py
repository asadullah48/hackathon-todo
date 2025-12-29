"""Task schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Request schema for creating a task."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    is_completed: bool = False


class TaskUpdate(BaseModel):
    """Request schema for updating a task."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    is_completed: bool | None = None


class TaskResponse(BaseModel):
    """Response schema for a task."""

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response schema for a list of tasks."""

    tasks: list[TaskResponse]
    total: int
