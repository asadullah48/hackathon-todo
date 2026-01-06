"""Authentication service."""
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.user import User
from src.schemas.user import UserCreate, UserLogin, UserResponse
from src.utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)


class AuthService:
    """Service for user authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the auth service."""
        self.db = db

    async def register(
        self,
        data: UserCreate,
    ) -> tuple[User, str, datetime]:
        """Register a new user."""
        # Check if email already exists
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError("Email already registered")

        # Create new user
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Create access token
        token, expires_at = create_access_token({
            "user_id": str(user.id),
            "email": user.email,
        })

        return user, token, expires_at

    async def login(
        self,
        data: UserLogin,
    ) -> tuple[User, str, datetime]:
        """Login an existing user."""
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid credentials")

        # Create access token
        token, expires_at = create_access_token({
            "user_id": str(user.id),
            "email": user.email,
        })

        return user, token, expires_at

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get a user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    def create_auth_response(
        self,
        user: User,
        token: str,
        expires_at: datetime
    ) -> dict:
        """Create authentication response dict matching AuthResponse schema."""
        return {
            "user": UserResponse.model_validate(user),
            "token": token,
            "expires_at": expires_at,
        }
