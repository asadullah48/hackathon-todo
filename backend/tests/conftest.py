"""Pytest configuration and shared fixtures."""

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
