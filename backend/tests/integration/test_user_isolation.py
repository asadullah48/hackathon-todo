"""Integration tests for User Isolation (User Story 5).

Tests cover ISO-01 through ISO-05 from test specification:
- Verify users cannot access each other's tasks
- Verify cross-user operations return 404 (not 403 for security)
"""

import pytest
import uuid
from httpx import AsyncClient


def get_auth_header(token: str) -> dict:
    """Generate authorization header with Bearer token."""
    return {"Authorization": f"Bearer {token}"}


class TestUserIsolation:
    """Tests to verify users can only access their own tasks."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_see_user_bs_tasks(self, client: AsyncClient):
        """ISO-01: User A creates task, User B lists tasks - User B sees empty list."""
        # Create User A
        email_a = f"usera_{uuid.uuid4().hex[:8]}@example.com"
        reg_a = await client.post(
            "/api/auth/register",
            json={"email": email_a, "password": "password123", "name": "User A"},
        )
        token_a = reg_a.json()["token"]

        # Create User B
        email_b = f"userb_{uuid.uuid4().hex[:8]}@example.com"
        reg_b = await client.post(
            "/api/auth/register",
            json={"email": email_b, "password": "password123", "name": "User B"},
        )
        token_b = reg_b.json()["token"]

        # User A creates a task
        await client.post(
            "/api/tasks",
            json={"title": "User A's private task"},
            headers=get_auth_header(token_a),
        )

        # User B lists tasks - should see empty list
        list_response = await client.get(
            "/api/tasks",
            headers=get_auth_header(token_b),
        )
        assert list_response.status_code == 200
        data = list_response.json()
        # User B should not see User A's task
        task_titles = [t["title"] for t in data["tasks"]]
        assert "User A's private task" not in task_titles

    @pytest.mark.asyncio
    async def test_user_a_cannot_get_user_bs_task(self, client: AsyncClient):
        """ISO-02: User A tries to get User B's task - returns 404."""
        # Create User A
        email_a = f"usera2_{uuid.uuid4().hex[:8]}@example.com"
        reg_a = await client.post(
            "/api/auth/register",
            json={"email": email_a, "password": "password123", "name": "User A"},
        )
        token_a = reg_a.json()["token"]

        # Create User B and get their task ID
        email_b = f"userb2_{uuid.uuid4().hex[:8]}@example.com"
        reg_b = await client.post(
            "/api/auth/register",
            json={"email": email_b, "password": "password123", "name": "User B"},
        )
        token_b = reg_b.json()["token"]

        create_b = await client.post(
            "/api/tasks",
            json={"title": "User B's task"},
            headers=get_auth_header(token_b),
        )
        task_id = create_b.json()["id"]

        # User A tries to get User B's task
        response = await client.get(
            f"/api/tasks/{task_id}",
            headers=get_auth_header(token_a),
        )
        # Should return 404 (not 403) for security
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_a_cannot_update_user_bs_task(self, client: AsyncClient):
        """ISO-03: User A tries to update User B's task - returns 404."""
        email_a = f"usera3_{uuid.uuid4().hex[:8]}@example.com"
        reg_a = await client.post(
            "/api/auth/register",
            json={"email": email_a, "password": "password123", "name": "User A"},
        )
        token_a = reg_a.json()["token"]

        email_b = f"userb3_{uuid.uuid4().hex[:8]}@example.com"
        reg_b = await client.post(
            "/api/auth/register",
            json={"email": email_b, "password": "password123", "name": "User B"},
        )
        token_b = reg_b.json()["token"]

        create_b = await client.post(
            "/api/tasks",
            json={"title": "User B's task"},
            headers=get_auth_header(token_b),
        )
        task_id = create_b.json()["id"]

        # User A tries to update User B's task
        response = await client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Hacked title"},
            headers=get_auth_header(token_a),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_a_cannot_delete_user_bs_task(self, client: AsyncClient):
        """ISO-04: User A tries to delete User B's task - returns 404."""
        email_a = f"usera4_{uuid.uuid4().hex[:8]}@example.com"
        reg_a = await client.post(
            "/api/auth/register",
            json={"email": email_a, "password": "password123", "name": "User A"},
        )
        token_a = reg_a.json()["token"]

        email_b = f"userb4_{uuid.uuid4().hex[:8]}@example.com"
        reg_b = await client.post(
            "/api/auth/register",
            json={"email": email_b, "password": "password123", "name": "User B"},
        )
        token_b = reg_b.json()["token"]

        create_b = await client.post(
            "/api/tasks",
            json={"title": "User B's task"},
            headers=get_auth_header(token_b),
        )
        task_id = create_b.json()["id"]

        # User A tries to delete User B's task
        response = await client.delete(
            f"/api/tasks/{task_id}",
            headers=get_auth_header(token_a),
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_a_cannot_toggle_user_bs_task(self, client: AsyncClient):
        """ISO-05: User A tries to toggle User B's task - returns 404."""
        email_a = f"usera5_{uuid.uuid4().hex[:8]}@example.com"
        reg_a = await client.post(
            "/api/auth/register",
            json={"email": email_a, "password": "password123", "name": "User A"},
        )
        token_a = reg_a.json()["token"]

        email_b = f"userb5_{uuid.uuid4().hex[:8]}@example.com"
        reg_b = await client.post(
            "/api/auth/register",
            json={"email": email_b, "password": "password123", "name": "User B"},
        )
        token_b = reg_b.json()["token"]

        create_b = await client.post(
            "/api/tasks",
            json={"title": "User B's task"},
            headers=get_auth_header(token_b),
        )
        task_id = create_b.json()["id"]

        # User A tries to toggle User B's task
        response = await client.patch(
            f"/api/tasks/{task_id}/toggle",
            headers=get_auth_header(token_a),
        )
        assert response.status_code == 404

        # Verify the task is still incomplete (unchanged)
        get_response = await client.get(
            f"/api/tasks/{task_id}",
            headers=get_auth_header(token_b),
        )
        assert get_response.json()["is_completed"] is False
