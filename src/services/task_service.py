"""Task service providing business logic for task management."""

from src.models.task import Task


class TaskNotFoundError(Exception):
    """Raised when a task operation targets a non-existent ID."""

    def __init__(self, task_id: int) -> None:
        """Initialize with the task ID that was not found.

        Args:
            task_id: The ID of the task that was not found.
        """
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        """Initialize with a validation error message.

        Args:
            message: Description of the validation failure.
        """
        super().__init__(message)


class TaskService:
    """Service for managing todo tasks.

    Provides CRUD operations and status toggling for tasks.
    Tasks are stored in-memory and IDs are auto-generated sequentially.
    """

    def __init__(self) -> None:
        """Initialize the task service with empty task list and ID counter."""
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Create a new task with auto-generated ID.

        Args:
            title: Task title (1-200 characters, required).
            description: Optional task description (0-1000 characters).

        Returns:
            The created Task with auto-generated ID.

        Raises:
            ValidationError: If title is empty or exceeds 200 characters,
                or if description exceeds 1000 characters.
        """
        # Validation
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")
        if len(title) > 200:
            raise ValidationError("Title exceeds 200 characters")
        if len(description) > 1000:
            raise ValidationError("Description exceeds 1000 characters")

        # Create task with auto-generated ID
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task | None:
        """Retrieve a task by ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task if found, None otherwise.
        """
        return next((t for t in self._tasks if t.id == task_id), None)

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks in creation order.

        Returns:
            A copy of the task list.
        """
        return list(self._tasks)

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """Update task fields.

        Args:
            task_id: The ID of the task to update.
            title: New title (if provided, 1-200 characters).
            description: New description (if provided, 0-1000 characters).

        Returns:
            The updated Task.

        Raises:
            TaskNotFoundError: If task ID does not exist.
            ValidationError: If new title is empty or exceeds 200 characters,
                or if new description exceeds 1000 characters.
        """
        task = self.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)

        # Validate and update title if provided
        if title is not None:
            if not title or not title.strip():
                raise ValidationError("Title cannot be empty")
            if len(title) > 200:
                raise ValidationError("Title exceeds 200 characters")
            task.title = title

        # Validate and update description if provided
        if description is not None:
            if len(description) > 1000:
                raise ValidationError("Description exceeds 1000 characters")
            task.description = description

        return task

    def delete_task(self, task_id: int) -> None:
        """Remove a task permanently.

        Args:
            task_id: The ID of the task to delete.

        Raises:
            TaskNotFoundError: If task ID does not exist.
        """
        task = self.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        self._tasks.remove(task)

    def toggle_task(self, task_id: int) -> Task:
        """Toggle task completion status.

        Args:
            task_id: The ID of the task to toggle.

        Returns:
            The task with toggled completion status.

        Raises:
            TaskNotFoundError: If task ID does not exist.
        """
        task = self.get_task(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        task.completed = not task.completed
        return task
