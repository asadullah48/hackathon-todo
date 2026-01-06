"""Security utilities for password hashing and JWT tokens."""
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from src.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Truncate to 72 bytes to avoid bcrypt limitation
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    password_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))


def create_access_token(data: dict[str, str]) -> tuple[str, datetime]:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_expiry_days)

    # Use 'sub' (subject) for user_id as per JWT standard
    if "user_id" in to_encode:
        to_encode["sub"] = to_encode.pop("user_id")

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt, expire


def get_token_expiry() -> datetime:
    """Get the expiry datetime for a new token."""
    return datetime.now(UTC) + timedelta(days=settings.jwt_expiry_days)


def decode_access_token(token: str) -> dict[str, str] | None:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None
