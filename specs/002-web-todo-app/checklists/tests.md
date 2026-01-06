# Test Specification: Full-Stack Web Todo Application

**Purpose**: Define test cases for Phase 2 verification
**Created**: 2026-01-06
**Feature**: `specs/002-web-todo-app/spec.md`
**Input**: User stories and acceptance scenarios from spec.md

---

## Test Categories

### 1. Authentication Tests (User Story 1)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| AUTH-01 | Register with valid email/password | 201 Created, JWT token returned |
| AUTH-02 | Register with duplicate email | 409 Conflict, error message |
| AUTH-03 | Register with invalid email format | 400 Validation error |
| AUTH-04 | Register with short password | 400 Validation error |
| AUTH-05 | Login with correct credentials | 200 OK, JWT token returned |
| AUTH-06 | Login with wrong password | 401 Unauthorized |
| AUTH-07 | Login with non-existent email | 401 Unauthorized |
| AUTH-08 | Access /api/auth/me with valid token | 200 OK, user data returned |
| AUTH-09 | Access /api/auth/me without token | 401 Unauthorized |
| AUTH-10 | Access /api/auth/me with invalid token | 401 Unauthorized |

### 2. Task CRUD Tests (User Story 2)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| TASK-01 | Create task with title only | 201 Created, task returned with ID |
| TASK-02 | Create task with title and description | 201 Created, both fields saved |
| TASK-03 | Create task with empty title | 400 Validation error |
| TASK-04 | Create task with title > 200 chars | 400 Validation error |
| TASK-05 | Create task without auth token | 401 Unauthorized |
| TASK-06 | List all tasks | 200 OK, array of tasks returned |
| TASK-07 | List tasks with pagination | 200 OK, paginated response |
| TASK-08 | List tasks filtered by completion | 200 OK, filtered array |
| TASK-09 | Get task by valid ID | 200 OK, task returned |
| TASK-10 | Get task by invalid UUID format | 400 Validation error |
| TASK-11 | Get non-existent task | 404 Not Found |
| TASK-12 | Update task title | 200 OK, updated task returned |
| TASK-13 | Update task description | 200 OK, updated task returned |
| TASK-14 | Update task with empty title | 400 Validation error |
| TASK-15 | Update non-existent task | 404 Not Found |
| TASK-16 | Delete task | 204 No Content |
| TASK-17 | Delete non-existent task | 404 Not Found |
| TASK-18 | Toggle task completion | 200 OK, toggled task returned |
| TASK-19 | Toggle non-existent task | 404 Not Found |

### 3. User Isolation Tests (User Story 5)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| ISO-01 | User A creates task, User B lists tasks | User B sees empty list |
| ISO-02 | User A tries to get User B's task | 404 Not Found |
| ISO-03 | User A tries to update User B's task | 404 Not Found |
| ISO-04 | User A tries to delete User B's task | 404 Not Found |
| ISO-05 | User A toggles User B's task | 404 Not Found |

### 4. Data Persistence Tests (User Story 4)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PERS-01 | Create task, query database directly | Task exists in database |
| PERS-02 | Create task, restart app, list tasks | Task still exists |
| PERS-03 | Task timestamps are set correctly | created_at and updated_at populated |

### 5. API Documentation Tests (User Story 3)

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| DOC-01 | Access /docs | Swagger UI loads |
| DOC-02 | Access /openapi.json | Valid OpenAPI schema returned |
| DOC-03 | All endpoints documented | Schema contains all CRUD endpoints |

---

## Test Execution Requirements

### Backend Test Command

```bash
cd backend && python -m pytest tests/ -v --tb=short
```

### Required Test Coverage

- Authentication endpoints: 100%
- Task CRUD endpoints: 100%
- Error responses: 100%
- User isolation: 100%

### Test Data Setup

1. Create test database (SQLite for unit tests, PostgreSQL for integration)
2. Run migrations: `alembic upgrade head`
3. Seed test users if needed
4. Clean up after each test

---

## Test Environment Variables

```bash
DATABASE_URL="sqlite:///./test.db"  # or PostgreSQL test URL
BETTER_AUTH_SECRET="test-secret-key-for-testing-only"
JWT_SECRET_KEY="test-jwt-secret-key"
ACCESS_TOKEN_EXPIRY_SECONDS=604800  # 7 days
```

---

## Integration with CI/CD

- Run tests on every PR
- Fail build if any test fails
- Generate coverage report
- Block merge if coverage drops below 80%

---

## Test Files Structure

```
backend/tests/
├── conftest.py              # Shared fixtures (client, database)
├── unit/
│   ├── test_models.py       # SQLModel validation tests
│   ├── test_schemas.py      # Pydantic model tests
│   └── test_services.py     # Business logic tests
├── integration/
│   ├── test_auth_api.py     # Authentication endpoint tests
│   ├── test_tasks_api.py    # Task CRUD endpoint tests
│   └── test_user_isolation.py # Cross-user access tests
└── contract/
    └── openapi_validation.py # OpenAPI schema compliance
```

---

## Validation Criteria

Phase 2 is complete when:

- [ ] All AUTH tests pass
- [ ] All TASK tests pass
- [ ] All ISO tests pass
- [ ] All PERS tests pass
- [ ] All DOC tests pass
- [ ] Code coverage >= 80%
- [ ] No linting errors
- [ ] Type checking passes (mypy/pyright)
