"""Task service for CRUD operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task
from src.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate


class TaskService:
    """Service for task CRUD operations."""

    def __init__(self, session: AsyncSession, user_id: UUID) -> None:
        self.session = session
        self.user_id = user_id

    async def create(self, data: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(
            user_id=self.user_id,
            title=data.title,
            description=data.description,
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def list(
        self,
        page: int = 1,
        page_size: int = 50,
        is_completed: Optional[bool] = None,
    ) -> TaskListResponse:
        """List all tasks for the current user."""
        # Build query
        query = select(Task).where(Task.user_id == self.user_id)

        if is_completed is not None:
            query = query.where(Task.is_completed == is_completed)

        # Get total count
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = query.order_by(Task.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return TaskListResponse(
            tasks=[TaskResponse.model_validate(t) for t in tasks],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get(self, task_id: UUID) -> Optional[Task]:
        """Get a task by ID for the current user."""
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == self.user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update(self, task_id: UUID, data: TaskUpdate) -> Optional[Task]:
        """Update a task."""
        task = await self.get(task_id)
        if not task:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)

        task.update_timestamp()
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: UUID) -> bool:
        """Delete a task."""
        task = await self.get(task_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.flush()
        return True

    async def toggle(self, task_id: UUID) -> Optional[Task]:
        """Toggle task completion status."""
        task = await self.get(task_id)
        if not task:
            return None

        task.is_completed = not task.is_completed
        task.update_timestamp()
        await self.session.flush()
        await self.session.refresh(task)
        return task
