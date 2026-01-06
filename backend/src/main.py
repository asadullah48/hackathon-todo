"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api.auth import router as auth_router
from src.api.chat import router as chat_router
from src.api.tasks import router as tasks_router
from src.config import get_settings
from src.database import init_db
from src.schemas.error import ErrorCode, ErrorResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup: initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Todo App API",
    description="""
Full-Stack Web Todo Application REST API.

## Features

* **Authentication** - JWT-based user registration and login
* **Tasks** - Full CRUD operations for todo items
* **Pagination** - Efficient list pagination for tasks
* **Filtering** - Filter tasks by completion status

## Authentication

All task endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-token>
```

Tokens are valid for 7 days after login.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and session management",
        },
        {
            "name": "Tasks",
            "description": "CRUD operations for todo items",
        },
        {
            "name": "chat",
            "description": "AI-powered chatbot for task management",
        },
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(ValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    details = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details[field] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid input data",
            details=details,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle uncaught exceptions."""
    message = str(exc) if settings.debug else "An unexpected error occurred"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            code=ErrorCode.INTERNAL_ERROR,
            message=message,
        ).model_dump(),
    )


# Register API routers
app.include_router(auth_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(chat_router)  # /api/chat prefix is defined in router


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
