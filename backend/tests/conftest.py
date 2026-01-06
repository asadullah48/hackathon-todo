"""Pytest configuration and shared fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.database import get_session
from src.main import app
from src.database import engine


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_engine():
    """Create async engine for tests."""
    # Use SQLite for testing
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for tests."""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(async_session: AsyncSession):
    """Create a test user in the database."""
    from src.models.user import User
    from src.utils.security import hash_password
    from uuid import uuid4

    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password=hash_password("password123"),
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
async def auth_token(test_user) -> str:
    """Generate JWT token for test user."""
    from src.utils.security import create_access_token

    return create_access_token(str(test_user.id))
