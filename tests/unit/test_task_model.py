"""Unit tests for the Task model."""

import pytest
from datetime import datetime

from src.models.task import Task


class TestTaskCreation:
    """Tests for Task creation and validation."""

    def test_create_valid_task(self) -> None:
        """Test creating a task with valid attributes."""
        task = Task(id=1, title="Buy groceries")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_create_task_with_description(self) -> None:
        """Test creating a task with title and description."""
        task = Task(id=1, title="Buy groceries", description="Milk, eggs, bread")
        assert task.description == "Milk, eggs, bread"

    def test_create_task_with_completed_status(self) -> None:
        """Test creating a task with completed=True."""
        task = Task(id=1, title="Done task", completed=True)
        assert task.completed is True

    def test_create_task_with_max_title_length(self) -> None:
        """Test creating a task with exactly 200 character title."""
        title = "a" * 200
        task = Task(id=1, title=title)
        assert len(task.title) == 200

    def test_create_task_with_max_description_length(self) -> None:
        """Test creating a task with exactly 1000 character description."""
        description = "b" * 1000
        task = Task(id=1, title="Test", description=description)
        assert len(task.description) == 1000


class TestTaskValidation:
    """Tests for Task validation errors."""

    def test_invalid_id_zero(self) -> None:
        """Test that id=0 raises ValueError."""
        with pytest.raises(ValueError, match="Invalid task ID"):
            Task(id=0, title="Test")

    def test_invalid_id_negative(self) -> None:
        """Test that negative id raises ValueError."""
        with pytest.raises(ValueError, match="Invalid task ID"):
            Task(id=-1, title="Test")

    def test_empty_title(self) -> None:
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="")

    def test_whitespace_only_title(self) -> None:
        """Test that whitespace-only title raises ValueError."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            Task(id=1, title="   ")

    def test_title_exceeds_max_length(self) -> None:
        """Test that title > 200 chars raises ValueError."""
        title = "a" * 201
        with pytest.raises(ValueError, match="Title exceeds 200 characters"):
            Task(id=1, title=title)

    def test_description_exceeds_max_length(self) -> None:
        """Test that description > 1000 chars raises ValueError."""
        description = "b" * 1001
        with pytest.raises(ValueError, match="Description exceeds 1000 characters"):
            Task(id=1, title="Test", description=description)


class TestTaskAttributes:
    """Tests for Task attribute behavior."""

    def test_task_is_mutable(self) -> None:
        """Test that task attributes can be modified."""
        task = Task(id=1, title="Original")
        task.title = "Modified"
        task.completed = True
        assert task.title == "Modified"
        assert task.completed is True

    def test_special_characters_in_title(self) -> None:
        """Test that special characters are allowed in title."""
        task = Task(id=1, title="Buy @#$% groceries! (urgent)")
        assert task.title == "Buy @#$% groceries! (urgent)"

    def test_unicode_in_title(self) -> None:
        """Test that unicode characters are allowed in title."""
        task = Task(id=1, title="买东西 🛒")
        assert task.title == "买东西 🛒"
