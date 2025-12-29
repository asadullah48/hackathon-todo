"""Authentication schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response schema for authentication."""

    user_id: UUID
    email: str
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
