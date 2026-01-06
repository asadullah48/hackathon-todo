# Code Review Checklist: Full-Stack Web Todo Application

**Purpose**: Validate implementation matches specification
**Created**: 2026-01-06
**Feature**: `specs/002-web-todo-app/spec.md`, `specs/002-web-todo-app/data-model.md`

---

## SQLModel Validation

### User Model (`backend/src/models/user.py`)

| Check | Description | Expected |
|-------|-------------|----------|
| [ ] Table name | Must be `__tablename__ = "users"` | `"users"` |
| [ ] Primary key | `id: UUID = Field(default_factory=uuid4, primary_key=True)` | UUID type |
| [ ] Email field | `email: EmailStr = Field(unique=True, index=True)` | Valid email, unique, indexed |
| [ ] Password field | `hashed_password: str` | String type, no plaintext |
| [ ] Timestamps | `created_at` and `updated_at` as datetime | datetime type |

### Task Model (`backend/src/models/task.py`)

| Check | Description | Expected |
|-------|-------------|----------|
| [ ] Table name | Must be `__tablename__ = "tasks"` | `"tasks"` |
| [ ] Primary key | `id: UUID = Field(default_factory=uuid4, primary_key=True)` | UUID type |
| [ ] Foreign key | `user_id: UUID = Field(foreign_key="users.id", index=True)` | FK to users |
| [ ] Title field | `title: str = Field(max_length=200)` | Max 200 chars |
| [ ] Description | `description: str \| None = Field(default=None, max_length=1000)` | Optional, max 1000 |
| [ ] Completion | `is_completed: bool = Field(default=False)` | Boolean default False |
| [ ] Timestamps | `created_at` and `updated_at` as datetime | datetime type |

### Relationship Syntax (SQLModel Correct)

```python
# ✅ CORRECT: Self-referential relationship
parent_task: "Task" = Relationship(
    back_populates="child_tasks",
    sa_relationship_kwargs={"remote_side": "Task.id"}
)

# ❌ INCORRECT: Using remote_columns (SQLAlchemy syntax, not SQLModel)
parent_task: "Task" = Relationship(
    back_populates="child_tasks",
    remote_columns=[id],  # WRONG - not valid SQLModel
    sa_relationship_kwargs={"remote_side": "Task.id"}
)
```

**Rule**: SQLModel uses `sa_relationship_kwargs` for SQLAlchemy options. Do NOT use `remote_columns` directly.

---

## API Endpoint Validation

### Auth Endpoints (`backend/src/api/auth.py`)

| Endpoint | Method | Status Code | Response |
|----------|--------|-------------|----------|
| `/api/auth/register` | POST | 201 | AuthResponse |
| `/api/auth/login` | POST | 200 | AuthResponse |
| `/api/auth/logout` | POST | 200 | {"message": ...} |
| `/api/auth/me` | GET | 200 | UserResponse |

### Task Endpoints (`backend/src/api/tasks.py`)

| Endpoint | Method | Status Code | Response |
|----------|--------|-------------|----------|
| `/api/tasks` | GET | 200 | TaskListResponse |
| `/api/tasks` | POST | 201 | TaskResponse |
| `/api/tasks/{id}` | GET | 200 | TaskResponse |
| `/api/tasks/{id}` | PUT | 200 | TaskResponse |
| `/api/tasks/{id}` | DELETE | 204 | None |
| `/api/tasks/{id}/toggle` | PATCH | 200 | TaskResponse |

---

## JWT Validation

| Check | Description | Expected |
|-------|-------------|----------|
| [ ] Token creation | Uses `jwt.encode()` with secret | HMAC-SHA256 |
| [ ] Token expiry | Expires after 7 days (604800 seconds) | Configurable |
| [ ] Token verification | Decodes and verifies signature | Returns user_id |
| [ ] Header format | `Authorization: Bearer <token>` | Standard format |

---

## Error Response Format

All errors must follow this format:

```python
{
    "code": "ERROR_CODE_STRING",
    "message": "Human-readable message",
    "details": { ... }  # Optional field-level errors
}
```

| Error Code | HTTP Status | Scenario |
|------------|-------------|----------|
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Invalid or missing token |
| `EMAIL_EXISTS` | 409 | Duplicate email on register |
| `INVALID_CREDENTIALS` | 401 | Wrong password on login |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Security Checklist

| Check | Description |
|-------|-------------|
| [ ] Passwords hashed | Never store plaintext passwords |
| [ ] JWT secret from env | Never hardcode secrets |
| [ ] CORS configured | Only allow frontend origin |
| [ ] Security headers | X-Content-Type-Options, X-Frame-Options |
| [ ] Input validation | All inputs validated with Pydantic |
| [ ] User isolation | All queries filter by user_id |

---

## Frontend Validation

| Check | Description |
|-------|-------------|
| [ ] Token stored | localStorage with 'access_token' key |
| [ ] Token attached | Authorization header with Bearer prefix |
| [ ] Protected routes | Middleware redirects to login |
| [ ] Error handling | Shows error messages to user |
| [ ] Loading states | Shows spinner during API calls |
| [ ] Responsive design | Works on mobile and desktop |

---

## Test Execution

```bash
# Run all tests
cd backend && python -m pytest tests/ -v

# Run with coverage
cd backend && python -m pytest tests/ --cov=src --cov-report=term-missing

# Lint
cd backend && ruff check src/
cd frontend && npm run lint

# Type check
cd backend && python -m mypy src/
cd frontend && npx tsc --noEmit
```

---

## Common Issues to Watch

### Import Errors

```python
# ❌ WRONG: Wrong import
from src.models import Task

# ✅ CORRECT: Import from specific module
from src.models.task import Task
```

### SQLModel Relationships

```python
# ❌ WRONG: SQLAlchemy syntax
remote_columns=[id]

# ✅ CORRECT: SQLModel syntax
sa_relationship_kwargs={"remote_side": "Task.id"}
```

### Environment Variables

```python
# ❌ WRONG: Hardcoded values
SECRET = "my-secret"

# ✅ CORRECT: From environment
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    jwt_secret_key: str
```

---

## Sign-off Criteria

- [ ] All SQLModel checks passed
- [ ] All API endpoints return correct status codes
- [ ] JWT authentication working
- [ ] User isolation verified
- [ ] All security checks passed
- [ ] Tests passing with 80%+ coverage
- [ ] No linting errors
- [ ] Type checking passes
