"""Contract tests for OpenAPI specification.

Tests cover DOC-01 through DOC-03 from test specification:
- Verify Swagger UI is accessible
- Verify OpenAPI schema is valid
- Verify all endpoints are documented
"""

import pytest
from httpx import AsyncClient


class TestOpenAPIDocumentation:
    """Tests for API documentation endpoints."""

    @pytest.mark.asyncio
    async def test_swagger_ui_accessible(self, client: AsyncClient):
        """DOC-01: Access /docs returns Swagger UI."""
        response = await client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_openapi_json_valid(self, client: AsyncClient):
        """DOC-02: Access /openapi.json returns valid OpenAPI schema."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    @pytest.mark.asyncio
    async def test_all_endpoints_documented(self, client: AsyncClient):
        """DOC-03: All CRUD endpoints are documented in OpenAPI schema."""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        paths = data.get("paths", {})

        # Auth endpoints
        assert "/api/auth/register" in paths
        assert "/api/auth/login" in paths
        assert "/api/auth/logout" in paths
        assert "/api/auth/me" in paths

        # Task CRUD endpoints
        assert "/api/tasks" in paths
        assert "/api/tasks/{task_id}" in paths
        assert "/api/tasks/{task_id}/toggle" in paths
