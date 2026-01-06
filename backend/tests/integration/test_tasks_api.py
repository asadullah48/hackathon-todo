"""Integration tests for Task CRUD API endpoints.

Tests cover TASK-01 through TASK-19 from test specification:
- Create task with valid/invalid data
- List tasks with pagination and filtering
- Get task by ID
- Update task
- Delete task
- Toggle task completion
"""

import pytest
import uuid
from httpx import AsyncClient


def get_auth_header(token: str) -> dict:
    """Generate authorization header with Bearer token."""
    return {"Authorization": f"Bearer {token}"}


class TestCreateTask:
    """Tests for POST /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_create_task_with_title_only(self, client: AsyncClient, auth_token: str):
        """TASK-01: Create task with title only returns 201 with task."""
        response = await client.post(
            "/api/tasks",
            json={"title": "Buy groceries"},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Buy groceries"
        assert data["is_completed"] is False
        assert data.get("description") is None or data.get("description") == ""

    @pytest.mark.asyncio
    async def test_create_task_with_title_and_description(self, client: AsyncClient, auth_token: str):
        """TASK-02: Create task with title and description returns 201 with both saved."""
        response = await client.post(
            "/api/tasks",
            json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"

    @pytest.mark.asyncio
    async def test_create_task_with_empty_title(self, client: AsyncClient, auth_token: str):
        """TASK-03: Create task with empty title returns 400 validation error."""
        response = await client.post(
            "/api/tasks",
            json={"title": ""},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_task_with_title_too_long(self, client: AsyncClient, auth_token: str):
        """TASK-04: Create task with title > 200 chars returns 400 validation error."""
        long_title = "a" * 201
        response = await client.post(
            "/api/tasks",
            json={"title": long_title},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_task_without_auth_token(self, client: AsyncClient):
        """TASK-05: Create task without auth token returns 401 Unauthorized."""
        response = await client.post(
            "/api/tasks",
            json={"title": "Buy groceries"},
        )
        assert response.status_code == 401


class TestListTasks:
    """Tests for GET /api/tasks endpoint."""

    @pytest.mark.asyncio
    async def test_list_all_tasks(self, client: AsyncClient, auth_token: str):
        """TASK-06: List all tasks returns 200 with array of tasks."""
        # Create some tasks first
        for title in ["Task 1", "Task 2", "Task 3"]:
            await client.post(
                "/api/tasks",
                json={"title": title},
                headers=get_auth_header(auth_token),
            )

        response = await client.get(
            "/api/tasks",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert data["total"] >= 3

    @pytest.mark.asyncio
    async def test_list_tasks_with_pagination(self, client: AsyncClient, auth_token: str):
        """TASK-07: List tasks with pagination returns paginated response."""
        # Create multiple tasks
        for i in range(5):
            await client.post(
                "/api/tasks",
                json={"title": f"Task {i}"},
                headers=get_auth_header(auth_token),
            )

        response = await client.get(
            "/api/tasks?page=1&page_size=2",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) <= 2
        assert "page" in data
        assert "page_size" in data

    @pytest.mark.asyncio
    async def test_list_tasks_filtered_by_completion(self, client: AsyncClient, auth_token: str):
        """TASK-08: List tasks filtered by completion status returns filtered array."""
        # Create tasks with different completion status
        response = await client.get(
            "/api/tasks?is_completed=false",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 200
        data = response.json()
        # All returned tasks should be incomplete


class TestGetTask:
    """Tests for GET /api/tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_task_by_valid_id(self, client: AsyncClient, auth_token: str):
        """TASK-09: Get task by valid ID returns 200 with task."""
        # Create a task first
        create_response = await client.post(
            "/api/tasks",
            json={"title": "Test Task"},
            headers=get_auth_header(auth_token),
        )
        task_id = create_response.json()["id"]

        response = await client.get(
            f"/api/tasks/{task_id}",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"

    @pytest.mark.asyncio
    async def test_get_task_by_invalid_uuid_format(self, client: AsyncClient, auth_token: str):
        """TASK-10: Get task with invalid UUID format returns 400 validation error."""
        response = await client.get(
            "/api/tasks/not-a-uuid",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, client: AsyncClient, auth_token: str):
        """TASK-11: Get non-existent task returns 404 Not Found."""
        fake_id = str(uuid.uuid4())
        response = await client.get(
            f"/api/tasks/{fake_id}",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "NOT_FOUND"


class TestUpdateTask:
    """Tests for PUT /api/tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_task_title(self, client: AsyncClient, auth_token: str):
        """TASK-12: Update task title returns 200 with updated task."""
        # Create a task
        create_response = await client.post(
            "/api/tasks",
            json={"title": "Original Title"},
            headers=get_auth_header(auth_token),
        )
        task_id = create_response.json()["id"]

        response = await client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Updated Title"},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_task_description(self, client: AsyncClient, auth_token: str):
        """TASK-13: Update task description returns 200 with updated task."""
        create_response = await client.post(
            "/api/tasks",
            json={"title": "Task", "description": "Original description"},
            headers=get_auth_header(auth_token),
        )
        task_id = create_response.json()["id"]

        response = await client.put(
            f"/api/tasks/{task_id}",
            json={"description": "Updated description"},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_task_with_empty_title(self, client: AsyncClient, auth_token: str):
        """TASK-14: Update task with empty title returns 400 validation error."""
        create_response = await client.post(
            "/api/tasks",
            json={"title": "Task"},
            headers=get_auth_header(auth_token),
        )
        task_id = create_response.json()["id"]

        response = await client.put(
            f"/api/tasks/{task_id}",
            json={"title": ""},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_nonexistent_task(self, client: AsyncClient, auth_token: str):
        """TASK-15: Update non-existent task returns 404 Not Found."""
        fake_id = str(uuid.uuid4())
        response = await client.put(
            f"/api/tasks/{fake_id}",
            json={"title": "New Title"},
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 404


class TestDeleteTask:
    """Tests for DELETE /api/tasks/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_task(self, client: AsyncClient, auth_token: str):
        """TASK-16: Delete task returns 204 No Content."""
        create_response = await client.post(
            "/api/tasks",
            json={"title": "Task to delete"},
            headers=get_auth_header(auth_token),
        )
        task_id = create_response.json()["id"]

        response = await client.delete(
            f"/api/tasks/{task_id}",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 204

        # Verify task is deleted
        get_response = await client.get(
            f"/api/tasks/{task_id}",
            headers=get_auth_header(auth_token),
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, client: AsyncClient, auth_token: str):
        """TASK-17: Delete non-existent task returns 404 Not Found."""
        fake_id = str(uuid.uuid4())
        response = await client.delete(
            f"/api/tasks/{fake_id}",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 404


class TestToggleTask:
    """Tests for PATCH /api/tasks/{id}/toggle endpoint."""

    @pytest.mark.asyncio
    async def test_toggle_task_completion(self, client: AsyncClient, auth_token: str):
        """TASK-18: Toggle task completion returns 200 with toggled task."""
        create_response = await client.post(
            "/api/tasks",
            json={"title": "Task to toggle"},
            headers=get_auth_header(auth_token),
        )
        task_id = create_response.json()["id"]
        assert create_response.json()["is_completed"] is False

        toggle_response = await client.patch(
            f"/api/tasks/{task_id}/toggle",
            headers=get_auth_header(auth_token),
        )
        assert toggle_response.status_code == 200
        assert toggle_response.json()["is_completed"] is True

        # Toggle again
        toggle_response2 = await client.patch(
            f"/api/tasks/{task_id}/toggle",
            headers=get_auth_header(auth_token),
        )
        assert toggle_response2.json()["is_completed"] is False

    @pytest.mark.asyncio
    async def test_toggle_nonexistent_task(self, client: AsyncClient, auth_token: str):
        """TASK-19: Toggle non-existent task returns 404 Not Found."""
        fake_id = str(uuid.uuid4())
        response = await client.patch(
            f"/api/tasks/{fake_id}/toggle",
            headers=get_auth_header(auth_token),
        )
        assert response.status_code == 404
