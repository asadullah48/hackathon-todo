"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import CurrentUserDep, SessionDep
from src.schemas.error import ErrorCode, ErrorResponse
from src.schemas.user import AuthResponse, UserCreate, UserLogin, UserResponse
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Email already registered"},
    },
)
async def register(data: UserCreate, session: SessionDep) -> AuthResponse:
    """
    Register a new user account.

    Creates a new user with email and password. Returns a JWT token valid for 7 days.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    """
    service = AuthService(session)

    try:
        user, token, expires_at = await service.register(data)
        return service.create_auth_response(user, token, expires_at)
    except ValueError as e:
        if "already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": ErrorCode.EMAIL_EXISTS,
                    "message": "Email already registered",
                },
            )
        raise


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(data: UserLogin, session: SessionDep) -> AuthResponse:
    """
    Authenticate with email and password.

    Returns a JWT token valid for 7 days. Store this token and include it
    in the Authorization header for subsequent requests.
    """
    service = AuthService(session)

    try:
        user, token, expires_at = await service.login(data)
        return service.create_auth_response(user, token, expires_at)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.INVALID_CREDENTIALS,
                "message": "Invalid email or password",
            },
        )


@router.post(
    "/logout",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def logout(_current_user_id: CurrentUserDep) -> dict[str, str]:
    """Logout current user (client should discard token)."""
    return {"message": "Logged out successfully"}


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def get_current_user(
    current_user_id: CurrentUserDep,
    session: SessionDep,
) -> UserResponse:
    """Get current authenticated user's profile."""
    service = AuthService(session)
    user = await service.get_user_by_id(current_user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.UNAUTHORIZED,
                "message": "User not found",
            },
        )

    return UserResponse.model_validate(user)
