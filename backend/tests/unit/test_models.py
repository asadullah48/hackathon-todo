"""Unit tests for SQLModel validation and Pydantic schemas."""

import pytest
from datetime import datetime
from uuid import uuid4


class TestTaskModelValidation:
    """Unit tests for Task model validation."""

    def test_task_requires_title(self):
        """Task title is required."""
        from src.models.task import Task
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Task(
                user_id=uuid4(),
                title="",  # Empty title should fail
            )

    def test_task_title_max_length(self):
        """Task title cannot exceed 200 characters."""
        from src.models.task import Task

        # 200 chars should work
        task = Task(
            user_id=uuid4(),
            title="a" * 200,
        )
        assert len(task.title) == 200

    def test_task_description_optional(self):
        """Task description is optional."""
        from src.models.task import Task

        task = Task(
            user_id=uuid4(),
            title="Test task",
        )
        assert task.description is None

    def test_task_description_max_length(self):
        """Task description cannot exceed 1000 characters."""
        from src.models.task import Task
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Task(
                user_id=uuid4(),
                title="Test",
                description="b" * 1001,
            )

    def test_task_defaults_to_incomplete(self):
        """New tasks default to is_completed=False."""
        from src.models.task import Task

        task = Task(
            user_id=uuid4(),
            title="Test task",
        )
        assert task.is_completed is False

    def test_task_has_timestamps(self):
        """Task has created_at and updated_at timestamps."""
        from src.models.task import Task

        task = Task(
            user_id=uuid4(),
            title="Test task",
        )
        assert task.created_at is not None
        assert task.updated_at is not None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)


class TestUserModelValidation:
    """Unit tests for User model validation."""

    def test_user_requires_email(self):
        """User email is required."""
        from src.models.user import User
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            User(
                email="",
                hashed_password="hashedpassword",
            )

    def test_user_requires_hashed_password(self):
        """User hashed_password is required."""
        from src.models.user import User
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            User(
                email="test@example.com",
                hashed_password="",
            )

    def test_user_has_timestamps(self):
        """User has created_at and updated_at timestamps."""
        from src.models.user import User

        user = User(
            email="test@example.com",
            hashed_password="hashedpassword",
        )
        assert user.created_at is not None
        assert user.updated_at is not None


class TestTaskSchemas:
    """Unit tests for Task Pydantic schemas."""

    def test_task_create_valid(self):
        """TaskCreate schema validates correctly."""
        from src.schemas.task import TaskCreate

        task = TaskCreate(title="Test task", description="Optional description")
        assert task.title == "Test task"
        assert task.description == "Optional description"

    def test_task_create_title_required(self):
        """TaskCreate requires title."""
        from src.schemas.task import TaskCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_task_update_partial(self):
        """TaskUpdate allows partial updates."""
        from src.schemas.task import TaskUpdate

        update = TaskUpdate(title="New title")
        assert update.title == "New title"
        assert update.description is None  # Not provided

    def test_task_response_has_all_fields(self):
        """TaskResponse includes all required fields."""
        from src.schemas.task import TaskResponse
        from uuid import uuid4
        from datetime import datetime

        task_id = uuid4()
        now = datetime.utcnow()

        response = TaskResponse(
            id=task_id,
            title="Test",
            description=None,
            is_completed=False,
            created_at=now,
            updated_at=now,
        )
        assert response.id == task_id
        assert response.title == "Test"
        assert response.is_completed is False


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

    def test_user_login_valid(self):
        """UserLogin schema validates correctly."""
        from src.schemas.user import UserLogin

        login = UserLogin(email="test@example.com", password="password123")
        assert login.email == "test@example.com"
        assert login.password == "password123"

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

        auth_response = AuthResponse(
            token="jwt-token-here",
            user=user_response,
            expires_at=datetime.utcnow(),
        )
        assert auth_response.token == "jwt-token-here"
        assert auth_response.user.email == "test@example.com"
        assert auth_response.expires_at is not None
