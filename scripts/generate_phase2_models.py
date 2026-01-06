#!/usr/bin/env python3
"""
Code generator for Phase 2 data model.

Reads specs/002-web-todo-app/data-model.md and generates:
- backend/src/models/task.py
- backend/src/models/user.py
"""

from pathlib import Path


TASK_MODEL_TEMPLATE = '''"""Task database model."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship


class Task(SQLModel, table=True):
    """Task entity for todo items."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase 5: Advanced features
    due_date: Optional[datetime] = Field(default=None)
    reminder_at: Optional[datetime] = Field(default=None)
    recurrence_type: Optional[str] = Field(default=None, max_length=20)
    recurrence_interval: int = Field(default=1)
    recurrence_end_date: Optional[datetime] = Field(default=None)
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id")

    # Relationships - Note: SQLModel uses sa_relationship_kwargs for SQLAlchemy options
    parent_task: Optional["Task"] = Relationship(
        back_populates="child_tasks",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    child_tasks: list["Task"] = Relationship(back_populates="parent_task")
    notifications: list["Notification"] = Relationship(back_populates="task")

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
'''


def generate_task_model():
    """Generate the Task model file."""
    # Output to backend/src/models/task.py
    base_dir = Path(__file__).parent.parent
    output_path = base_dir / "backend" / "src" / "models" / "task.py"
    output_path.write_text(TASK_MODEL_TEMPLATE.strip() + "\n")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    generate_task_model()
