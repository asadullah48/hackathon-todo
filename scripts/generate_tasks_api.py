#!/usr/bin/env python3
"""
Code generator for Task API endpoints.

Generates backend/src/api/tasks.py
"""

from pathlib import Path


TASKS_API_TEMPLATE = '''"""Task API endpoints."""

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUserDep, SessionDep
from src.events import EventPublisher
from src.schemas.error import ErrorCode, ErrorResponse
from src.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from src.services.task import TaskService

TASK_EVENTS_TOPIC = "task-events"
REMINDER_TOPIC = "reminders"

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _build_event_payload(task: "Task") -> dict[str, Any]:
    return {
        "task_id": str(task.id),
        "user_id": str(task.user_id),
        "title": task.title,
        "description": task.description,
        "is_completed": task.is_completed,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "reminder_at": task.reminder_at.isoformat() if task.reminder_at else None,
        "recurrence_type": task.recurrence_type,
        "recurrence_interval": task.recurrence_interval,
        "recurrence_end_date": task.recurrence_end_date.isoformat() if task.recurrence_end_date else None,
        "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
        "updated_at": task.updated_at.isoformat(),
    }


def _should_schedule_reminder(task: "Task") -> bool:
    return bool(
        task.reminder_at
        and task.reminder_at > datetime.now(timezone.utc)
        and not task.is_completed
    )


def _should_cancel_reminder(task: "Task", previous: "Task | None") -> bool:
    if task.is_completed:
        return True
    if previous and previous.reminder_at and not task.reminder_at:
        return True
    if previous and previous.reminder_at != task.reminder_at:
        return True
    return False


def _should_publish_update(previous: "Task | None", current: "Task") -> bool:
    if not previous:
        return True
    tracked_fields = {
        "title",
        "description",
        "is_completed",
        "due_date",
        "reminder_at",
        "recurrence_type",
        "recurrence_interval",
        "recurrence_end_date",
    }
    return any(getattr(previous, f) != getattr(current, f) for f in tracked_fields)


def _schedule_reminder(task: "Task") -> None:
    if _should_schedule_reminder(task):
        asyncio.create_task(
            EventPublisher.schedule_reminder(
                task_id=task.id,
                user_id=str(task.user_id),
                task_title=task.title,
                remind_at=task.reminder_at,
            )
        )


def _cancel_reminder(task: "Task") -> None:
    asyncio.create_task(EventPublisher.cancel_reminder(task_id=task.id))


def _publish_event(event_type: str, task: "Task") -> None:
    asyncio.create_task(
        EventPublisher.publish(
            topic=TASK_EVENTS_TOPIC,
            event_type=event_type,
            data={"task": _build_event_payload(task)},
        )
    )


def _publish_reminder_event(task: "Task") -> None:
    asyncio.create_task(
        EventPublisher.publish(
            topic=REMINDER_TOPIC,
            event_type="reminder.due",
            data=_build_event_payload(task),
        )
    )


def _handle_reminder_changes(previous: "Task | None", current: "Task") -> None:
    if _should_schedule_reminder(current):
        _schedule_reminder(current)
    elif previous and _should_cancel_reminder(current, previous):
        _cancel_reminder(current)


def _handle_task_created(task: "Task") -> None:
    _publish_event("task.created", task)
    _handle_reminder_changes(None, task)


def _handle_task_updated(previous: "Task", current: "Task") -> None:
    if _should_publish_update(previous, current):
        event_type = "task.completed" if current.is_completed else "task.updated"
        _publish_event(event_type, current)
    _handle_reminder_changes(previous, current)


def _handle_task_deleted(task: "Task") -> None:
    _cancel_reminder(task)
    _publish_event("task.deleted", task)


@router.get(
    "/",
    response_model=TaskListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def list_tasks(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    is_completed: bool | None = Query(default=None),
) -> TaskListResponse:
    """List all tasks for the authenticated user."""
    service = TaskService(session, current_user_id)
    return await service.list(page=page, page_size=page_size, is_completed=is_completed)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def create_task(
    data: TaskCreate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> TaskResponse:
    """Create a new task."""
    service = TaskService(session, current_user_id)
    task = await service.create(data)
    _handle_task_created(task)
    return TaskResponse.model_validate(task)


async def _get_existing_task(service: TaskService, task_id: UUID) -> "Task":
    task = await service.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": ErrorCode.NOT_FOUND, "message": "Task not found"},
        )
    return task


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def get_task(
    task_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> TaskResponse:
    """Get a specific task by ID."""
    service = TaskService(session, current_user_id)
    task = await service.get(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": ErrorCode.NOT_FOUND,
                "message": "Task not found",
            },
        )

    return TaskResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> TaskResponse:
    """Update a task's title and/or description."""
    service = TaskService(session, current_user_id)
    task = await service.update(task_id, data)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": ErrorCode.NOT_FOUND,
                "message": "Task not found",
            },
        )

    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def delete_task(
    task_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> None:
    """Delete a task."""
    service = TaskService(session, current_user_id)
    deleted = await service.delete(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": ErrorCode.NOT_FOUND,
                "message": "Task not found",
            },
        )


@router.patch(
    "/{task_id}/toggle",
    response_model=TaskResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def toggle_task(
    task_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> TaskResponse:
    """Toggle task completion status."""
    service = TaskService(session, current_user_id)
    task = await service.toggle(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": ErrorCode.NOT_FOUND,
                "message": "Task not found",
            },
        )

    return TaskResponse.model_validate(task)
'''


def generate_tasks_api():
    """Generate the Tasks API file."""
    base_dir = Path(__file__).parent.parent
    output_path = base_dir / "backend" / "src" / "api" / "tasks.py"
    output_path.write_text(TASKS_API_TEMPLATE.strip() + "\n")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate_tasks_api()
