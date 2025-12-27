"""Task model for the todo application."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Task:
    """Represents a todo item with validation.

    Attributes:
        id: Unique positive integer identifier (auto-generated, immutable).
        title: Required text (1-200 characters).
        description: Optional text (0-1000 characters).
        completed: Boolean indicating completion status (defaults to False).
        created_at: Timestamp when the task was created.
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate task attributes on creation."""
        if self.id <= 0:
            raise ValueError("Invalid task ID")
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title exceeds 200 characters")
        if len(self.description) > 1000:
            raise ValueError("Description exceeds 1000 characters")
