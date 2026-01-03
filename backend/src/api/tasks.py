"""Task API endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUserDep, SessionDep
from src.schemas.error import ErrorCode, ErrorResponse
from src.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from src.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
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
    return TaskResponse.model_validate(task)


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
