"""Integration tests for Authentication API endpoints.

Tests cover AUTH-01 through AUTH-10 from test specification:
- User registration with valid/invalid data
- User login with correct/wrong credentials
- Current user endpoint with/without token
"""

import pytest
import uuid
from httpx import AsyncClient


class TestUserRegistration:
    """Tests for POST /api/auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_with_valid_email_password(self, client: AsyncClient):
        """AUTH-01: Register with valid email/password returns 201 with JWT token."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": f"newuser_{uuid.uuid4().hex[:8]}@example.com",
                "password": "securepassword123",
                "name": "Test User",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_register_with_duplicate_email(self, client: AsyncClient):
        """AUTH-02: Register with duplicate email returns 409 Conflict."""
        email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"

        # First registration succeeds
        response1 = await client.post(
            "/api/auth/register",
            json={"email": email, "password": "password123", "name": "User 1"},
        )
        assert response1.status_code == 201

        # Second registration fails
        response2 = await client.post(
            "/api/auth/register",
            json={"email": email, "password": "password123", "name": "User 2"},
        )
        assert response2.status_code == 409
        data = response2.json()
        assert data["code"] == "EMAIL_EXISTS"

    @pytest.mark.asyncio
    async def test_register_with_invalid_email_format(self, client: AsyncClient):
        """AUTH-03: Register with invalid email format returns 400 validation error."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "password123"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_register_with_short_password(self, client: AsyncClient):
        """AUTH-04: Register with short password returns 400 validation error."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "short"},
        )
        assert response.status_code == 400


class TestUserLogin:
    """Tests for POST /api/auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_with_correct_credentials(self, client: AsyncClient):
        """AUTH-05: Login with correct credentials returns 200 with JWT token."""
        email = f"login_{uuid.uuid4().hex[:8]}@example.com"
        password = "mypassword123"

        # Register first
        await client.post(
            "/api/auth/register",
            json={"email": email, "password": password, "name": "Test"},
        )

        # Login succeeds
        response = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, client: AsyncClient):
        """AUTH-06: Login with wrong password returns 401 Unauthorized."""
        email = f"wrongpass_{uuid.uuid4().hex[:8]}@example.com"

        await client.post(
            "/api/auth/register",
            json={"email": email, "password": "correctpassword", "name": "Test"},
        )

        response = await client.post(
            "/api/auth/login",
            json={"email": email, "password": "wrongpassword"},
        )
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "INVALID_CREDENTIALS"

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email(self, client: AsyncClient):
        """AUTH-07: Login with non-existent email returns 401 Unauthorized."""
        response = await client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401


class TestCurrentUser:
    """Tests for GET /api/auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self, client: AsyncClient):
        """AUTH-08: Access /api/auth/me with valid token returns 200 with user data."""
        # Register and login
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": f"me_{uuid.uuid4().hex[:8]}@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
        token = register_response.json()["token"]

        # Get current user
        response = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, client: AsyncClient):
        """AUTH-09: Access /api/auth/me without token returns 401 Unauthorized."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self, client: AsyncClient):
        """AUTH-10: Access /api/auth/me with invalid token returns 401 Unauthorized."""
        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
