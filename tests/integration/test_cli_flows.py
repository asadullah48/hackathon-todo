"""Integration tests for full CLI flows."""

import pytest

from src.services.task_service import TaskService, TaskNotFoundError


class TestFullCrudFlow:
    """Test complete CRUD workflow: add -> view -> toggle -> update -> delete."""

    def test_complete_workflow(self) -> None:
        """Test the complete flow: add -> view -> toggle -> update -> delete."""
        service = TaskService()

        # Step 1: Add tasks
        task1 = service.add_task("Buy groceries", "Milk, eggs, bread")
        task2 = service.add_task("Call mom")

        assert task1.id == 1
        assert task2.id == 2
        assert task1.completed is False
        assert task2.completed is False

        # Step 2: View all tasks
        tasks = service.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].title == "Buy groceries"
        assert tasks[1].title == "Call mom"

        # Step 3: Toggle task 1 to complete
        toggled = service.toggle_task(1)
        assert toggled.completed is True

        # Verify task 2 is still incomplete
        task2_check = service.get_task(2)
        assert task2_check is not None
        assert task2_check.completed is False

        # Step 4: Update task 2
        updated = service.update_task(2, title="Call mom (urgent)", description="Before 5pm")
        assert updated.title == "Call mom (urgent)"
        assert updated.description == "Before 5pm"

        # Step 5: Delete task 1
        service.delete_task(1)

        # Verify deletion
        assert service.get_task(1) is None
        remaining = service.get_all_tasks()
        assert len(remaining) == 1
        assert remaining[0].id == 2


class TestQuickstartScenario:
    """Test the exact scenario from quickstart.md."""

    def test_quickstart_example_session(self) -> None:
        """Replicate the quickstart.md example session programmatically."""
        service = TaskService()

        # Add "Buy groceries" with description
        task1 = service.add_task("Buy groceries", "Milk, eggs, bread")
        assert task1.id == 1
        assert task1.title == "Buy groceries"
        assert task1.description == "Milk, eggs, bread"
        assert task1.completed is False

        # Add "Call mom" without description
        task2 = service.add_task("Call mom")
        assert task2.id == 2
        assert task2.title == "Call mom"
        assert task2.description == ""
        assert task2.completed is False

        # View tasks - both should be incomplete
        tasks = service.get_all_tasks()
        assert len(tasks) == 2
        assert all(not t.completed for t in tasks)

        # Toggle task 1 to complete
        toggled = service.toggle_task(1)
        assert toggled.completed is True

        # View tasks - task 1 complete, task 2 incomplete
        tasks = service.get_all_tasks()
        assert tasks[0].completed is True
        assert tasks[1].completed is False


class TestEdgeCases:
    """Test edge cases and error handling in workflows."""

    def test_toggle_back_to_incomplete(self) -> None:
        """Test toggling a completed task back to incomplete."""
        service = TaskService()
        task = service.add_task("Test task")

        # Toggle to complete
        service.toggle_task(task.id)
        assert service.get_task(task.id).completed is True  # type: ignore[union-attr]

        # Toggle back to incomplete
        service.toggle_task(task.id)
        assert service.get_task(task.id).completed is False  # type: ignore[union-attr]

    def test_update_preserves_unchanged_fields(self) -> None:
        """Test that update only changes specified fields."""
        service = TaskService()
        task = service.add_task("Original title", "Original description")

        # Update only title
        updated = service.update_task(task.id, title="New title")
        assert updated.title == "New title"
        assert updated.description == "Original description"

        # Update only description
        updated = service.update_task(task.id, description="New description")
        assert updated.title == "New title"
        assert updated.description == "New description"

    def test_deleted_task_id_not_reused(self) -> None:
        """Test that deleted task IDs are not reused."""
        service = TaskService()

        task1 = service.add_task("Task 1")  # ID 1
        task2 = service.add_task("Task 2")  # ID 2
        service.delete_task(task1.id)

        # New task should get ID 3, not reuse ID 1
        task3 = service.add_task("Task 3")
        assert task3.id == 3

    def test_operations_on_nonexistent_task(self) -> None:
        """Test that operations on nonexistent tasks raise errors."""
        service = TaskService()

        with pytest.raises(TaskNotFoundError):
            service.toggle_task(999)

        with pytest.raises(TaskNotFoundError):
            service.update_task(999, title="New")

        with pytest.raises(TaskNotFoundError):
            service.delete_task(999)

    def test_multiple_rapid_operations(self) -> None:
        """Test multiple operations in quick succession."""
        service = TaskService()

        # Add many tasks
        for i in range(10):
            service.add_task(f"Task {i + 1}")

        assert len(service.get_all_tasks()) == 10

        # Toggle all odd-numbered tasks
        for i in range(1, 11, 2):
            service.toggle_task(i)

        tasks = service.get_all_tasks()
        for task in tasks:
            if task.id % 2 == 1:
                assert task.completed is True
            else:
                assert task.completed is False

        # Delete all even-numbered tasks
        for i in range(2, 11, 2):
            service.delete_task(i)

        remaining = service.get_all_tasks()
        assert len(remaining) == 5
        assert all(t.id % 2 == 1 for t in remaining)
