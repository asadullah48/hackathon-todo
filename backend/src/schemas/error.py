"""Error response schemas for API."""


from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    code: str
    message: str
    details: dict[str, str] | None = None


class ErrorCode:
    """Error code constants."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    EMAIL_EXISTS = "EMAIL_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INTERNAL_ERROR = "INTERNAL_ERROR"
