"""Unit tests for SQLModel validation and Pydantic schemas.

Note: SQLModel models defer validation to database layer.
Pydantic schemas validate at construction time.
"""

import pytest
from datetime import datetime
from uuid import uuid4


class TestTaskSchemas:
    """Unit tests for Task Pydantic schemas (not SQLModel)."""

    def test_task_create_valid(self):
        """TaskCreate schema validates correctly."""
        from src.schemas.task import TaskCreate

        task = TaskCreate(title="Test task", description="Optional description")
        assert task.title == "Test task"
        assert task.description == "Optional description"

    def test_task_create_title_required(self):
        """TaskCreate requires title - empty string fails."""
        from src.schemas.task import TaskCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_task_create_title_min_length(self):
        """TaskCreate title min_length=1 allows whitespace (Pydantic behavior).

        Note: Pydantic's min_length=1 allows whitespace-only strings.
        Validation of meaningful content is done at API/service layer.
        """
        from src.schemas.task import TaskCreate

        # Whitespace-only passes Pydantic validation (min_length=1)
        # Real validation happens at API level or service layer
        task = TaskCreate(title="   ")
        assert task.title == "   "  # Pydantic allows this

    def test_task_create_title_max_length(self):
        """TaskCreate title max 200 characters."""
        from src.schemas.task import TaskCreate

        task = TaskCreate(title="a" * 200)
        assert len(task.title) == 200

    def test_task_create_title_exceeds_max(self):
        """TaskCreate title > 200 characters fails."""
        from src.schemas.task import TaskCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TaskCreate(title="a" * 201)

    def test_task_create_description_optional(self):
        """TaskCreate description is optional."""
        from src.schemas.task import TaskCreate

        task = TaskCreate(title="Test")
        assert task.description is None

    def test_task_create_description_max_length(self):
        """TaskCreate description max 1000 characters."""
        from src.schemas.task import TaskCreate

        task = TaskCreate(title="Test", description="b" * 1000)
        assert len(task.description) == 1000

    def test_task_create_description_exceeds_max(self):
        """TaskCreate description > 1000 characters fails."""
        from src.schemas.task import TaskCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TaskCreate(title="Test", description="b" * 1001)

    def test_task_update_partial(self):
        """TaskUpdate allows partial updates."""
        from src.schemas.task import TaskUpdate

        update = TaskUpdate(title="New title")
        assert update.title == "New title"
        assert update.description is None  # Not provided

    def test_task_response_with_all_fields(self):
        """TaskResponse includes all fields including Phase 5."""
        from src.schemas.task import TaskResponse

        task_id = uuid4()
        now = datetime.utcnow()

        response = TaskResponse(
            id=task_id,
            user_id=uuid4(),
            title="Test",
            description=None,
            is_completed=False,
            created_at=now,
            updated_at=now,
            due_date=None,
            reminder_at=None,
            recurrence_type=None,
            recurrence_interval=1,
            recurrence_end_date=None,
            parent_task_id=None,
        )
        assert response.id == task_id
        assert response.title == "Test"
        assert response.is_completed is False
        # Phase 5 fields
        assert response.due_date is None
        assert response.recurrence_interval == 1

    def test_task_list_response(self):
        """TaskListResponse format is correct (tasks + total only)."""
        from src.schemas.task import TaskListResponse

        response = TaskListResponse(
            tasks=[],
            total=0,
        )
        assert response.tasks == []
        assert response.total == 0
        # Note: Pagination fields (page, page_size) are not in the response
        # The API uses query params for pagination, not response fields


class TestUserSchemas:
    """Unit tests for User Pydantic schemas."""

    def test_user_create_valid(self):
        """UserCreate schema validates correctly."""
        from src.schemas.user import UserCreate

        user = UserCreate(email="test@example.com", password="securepassword123")
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"

    def test_user_create_invalid_email(self):
        """UserCreate rejects invalid email."""
        from src.schemas.user import UserCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="password123")

    def test_user_create_password_min_length(self):
        """UserCreate password min 8 characters."""
        from src.schemas.user import UserCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="short")

    def test_user_login_valid(self):
        """UserLogin schema validates correctly."""
        from src.schemas.user import UserLogin

        login = UserLogin(email="test@example.com", password="password123")
        assert login.email == "test@example.com"
        assert login.password == "password123"

    def test_user_response_has_required_fields(self):
        """UserResponse includes id, email, created_at."""
        from src.schemas.user import UserResponse
        from uuid import uuid4
        from datetime import datetime

        user_id = uuid4()
        now = datetime.utcnow()

        response = UserResponse(
            id=user_id,
            email="test@example.com",
            created_at=now,
        )
        assert response.id == user_id
        assert response.email == "test@example.com"
        assert response.created_at == now

    def test_auth_response_contains_token(self):
        """AuthResponse includes token, user, and expires_at."""
        from src.schemas.user import AuthResponse, UserResponse
        from uuid import uuid4
        from datetime import datetime

        user_response = UserResponse(
            id=uuid4(),
            email="test@example.com",
            created_at=datetime.utcnow(),
        )

        expires_at = datetime.utcnow()

        auth_response = AuthResponse(
            token="jwt-token-here",
            user=user_response,
            expires_at=expires_at,
        )
        assert auth_response.token == "jwt-token-here"
        assert auth_response.user.email == "test@example.com"
        assert auth_response.expires_at == expires_at


class TestErrorSchemas:
    """Unit tests for Error schemas."""

    def test_error_response_format(self):
        """ErrorResponse has correct format."""
        from src.schemas.error import ErrorResponse, ErrorCode

        error = ErrorResponse(
            code=ErrorCode.NOT_FOUND,
            message="Task not found",
        )
        assert error.code == ErrorCode.NOT_FOUND
        assert error.message == "Task not found"
        assert error.details is None

    def test_error_response_with_details(self):
        """ErrorResponse can include details."""
        from src.schemas.error import ErrorResponse, ErrorCode

        error = ErrorResponse(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid input",
            details={"title": "Field required"},
        )
        assert error.code == ErrorCode.VALIDATION_ERROR
        assert error.details == {"title": "Field required"}
