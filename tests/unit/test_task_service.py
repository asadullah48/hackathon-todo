"""Unit tests for the TaskService."""

import pytest

from src.models.task import Task
from src.services.task_service import TaskService, TaskNotFoundError, ValidationError


class TestAddTask:
    """Tests for TaskService.add_task method."""

    def test_add_task_with_title_only(self) -> None:
        """Test adding a task with just a title."""
        service = TaskService()
        task = service.add_task("Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == ""
        assert task.completed is False

    def test_add_task_with_title_and_description(self) -> None:
        """Test adding a task with title and description."""
        service = TaskService()
        task = service.add_task("Buy groceries", "Milk, eggs, bread")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"

    def test_add_multiple_tasks_sequential_ids(self) -> None:
        """Test that multiple tasks get sequential IDs."""
        service = TaskService()
        task1 = service.add_task("Task 1")
        task2 = service.add_task("Task 2")
        task3 = service.add_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_empty_title_raises_error(self) -> None:
        """Test that empty title raises ValidationError."""
        service = TaskService()
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            service.add_task("")

    def test_add_task_whitespace_title_raises_error(self) -> None:
        """Test that whitespace-only title raises ValidationError."""
        service = TaskService()
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            service.add_task("   ")

    def test_add_task_title_too_long_raises_error(self) -> None:
        """Test that title > 200 chars raises ValidationError."""
        service = TaskService()
        long_title = "a" * 201
        with pytest.raises(ValidationError, match="Title exceeds 200 characters"):
            service.add_task(long_title)

    def test_add_task_max_title_length_succeeds(self) -> None:
        """Test that title at 200 chars succeeds."""
        service = TaskService()
        max_title = "a" * 200
        task = service.add_task(max_title)
        assert len(task.title) == 200

    def test_add_task_description_too_long_raises_error(self) -> None:
        """Test that description > 1000 chars raises ValidationError."""
        service = TaskService()
        long_desc = "b" * 1001
        with pytest.raises(ValidationError, match="Description exceeds 1000 characters"):
            service.add_task("Valid title", long_desc)


class TestGetAllTasks:
    """Tests for TaskService.get_all_tasks method."""

    def test_get_all_tasks_empty_list(self) -> None:
        """Test getting tasks from empty service."""
        service = TaskService()
        tasks = service.get_all_tasks()
        assert tasks == []

    def test_get_all_tasks_returns_all(self) -> None:
        """Test getting all tasks returns complete list."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")
        service.add_task("Task 3")

        tasks = service.get_all_tasks()
        assert len(tasks) == 3
        assert [t.title for t in tasks] == ["Task 1", "Task 2", "Task 3"]

    def test_get_all_tasks_returns_copy(self) -> None:
        """Test that get_all_tasks returns a copy, not the original."""
        service = TaskService()
        service.add_task("Task 1")

        tasks = service.get_all_tasks()
        tasks.clear()

        # Original list should still have the task
        assert len(service.get_all_tasks()) == 1


class TestGetTask:
    """Tests for TaskService.get_task method."""

    def test_get_existing_task(self) -> None:
        """Test getting an existing task by ID."""
        service = TaskService()
        created = service.add_task("Test task")

        task = service.get_task(created.id)
        assert task is not None
        assert task.id == created.id
        assert task.title == "Test task"

    def test_get_nonexistent_task(self) -> None:
        """Test getting a task that doesn't exist."""
        service = TaskService()
        task = service.get_task(999)
        assert task is None


class TestToggleTask:
    """Tests for TaskService.toggle_task method."""

    def test_toggle_incomplete_to_complete(self) -> None:
        """Test toggling an incomplete task to complete."""
        service = TaskService()
        task = service.add_task("Test task")
        assert task.completed is False

        toggled = service.toggle_task(task.id)
        assert toggled.completed is True

    def test_toggle_complete_to_incomplete(self) -> None:
        """Test toggling a complete task back to incomplete."""
        service = TaskService()
        task = service.add_task("Test task")
        service.toggle_task(task.id)  # Now complete
        assert service.get_task(task.id).completed is True  # type: ignore[union-attr]

        toggled = service.toggle_task(task.id)
        assert toggled.completed is False

    def test_toggle_nonexistent_task_raises_error(self) -> None:
        """Test toggling a non-existent task raises error."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError, match="Task not found: 999"):
            service.toggle_task(999)


class TestUpdateTask:
    """Tests for TaskService.update_task method."""

    def test_update_title_only(self) -> None:
        """Test updating just the title."""
        service = TaskService()
        task = service.add_task("Original", "Description")

        updated = service.update_task(task.id, title="Updated")
        assert updated.title == "Updated"
        assert updated.description == "Description"  # Unchanged

    def test_update_description_only(self) -> None:
        """Test updating just the description."""
        service = TaskService()
        task = service.add_task("Title", "Original")

        updated = service.update_task(task.id, description="Updated")
        assert updated.title == "Title"  # Unchanged
        assert updated.description == "Updated"

    def test_update_both_title_and_description(self) -> None:
        """Test updating both title and description."""
        service = TaskService()
        task = service.add_task("Original Title", "Original Desc")

        updated = service.update_task(task.id, title="New Title", description="New Desc")
        assert updated.title == "New Title"
        assert updated.description == "New Desc"

    def test_update_nonexistent_task_raises_error(self) -> None:
        """Test updating a non-existent task raises error."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError, match="Task not found: 999"):
            service.update_task(999, title="New")

    def test_update_empty_title_raises_error(self) -> None:
        """Test updating with empty title raises error."""
        service = TaskService()
        task = service.add_task("Original")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            service.update_task(task.id, title="")

    def test_update_title_too_long_raises_error(self) -> None:
        """Test updating with title > 200 chars raises error."""
        service = TaskService()
        task = service.add_task("Original")

        with pytest.raises(ValidationError, match="Title exceeds 200 characters"):
            service.update_task(task.id, title="a" * 201)


class TestDeleteTask:
    """Tests for TaskService.delete_task method."""

    def test_delete_existing_task(self) -> None:
        """Test deleting an existing task."""
        service = TaskService()
        task = service.add_task("To delete")

        service.delete_task(task.id)
        assert service.get_task(task.id) is None

    def test_delete_nonexistent_task_raises_error(self) -> None:
        """Test deleting a non-existent task raises error."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError, match="Task not found: 999"):
            service.delete_task(999)

    def test_delete_removes_from_list(self) -> None:
        """Test that deleted task no longer appears in list."""
        service = TaskService()
        task1 = service.add_task("Task 1")
        task2 = service.add_task("Task 2")
        task3 = service.add_task("Task 3")

        service.delete_task(task2.id)

        tasks = service.get_all_tasks()
        assert len(tasks) == 2
        assert [t.id for t in tasks] == [1, 3]
