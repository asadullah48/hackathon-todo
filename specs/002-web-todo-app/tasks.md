# Tasks: Full-Stack Web Todo Application

**Input**: Design documents from `/specs/002-web-todo-app/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/auth.yaml, contracts/tasks.yaml

**Tests**: Tests are NOT explicitly requested - implementing without test-first approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` (FastAPI, Python 3.12+)
- **Frontend**: `frontend/src/` (Next.js 16+, TypeScript)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both frontend and backend

- [x] T001 Create backend project structure per plan.md in `backend/`
- [x] T002 [P] Initialize backend Python project with pyproject.toml in `backend/pyproject.toml`
- [x] T003 [P] Add FastAPI, SQLModel, Pydantic, asyncpg dependencies to `backend/pyproject.toml`
- [x] T004 [P] Create frontend project with Next.js 16+ in `frontend/`
- [x] T005 [P] Add TypeScript, Tailwind CSS, Better Auth to frontend in `frontend/package.json`
- [x] T006 [P] Configure Tailwind CSS in `frontend/tailwind.config.ts`
- [x] T007 [P] Configure TypeScript strict mode in `frontend/tsconfig.json`
- [x] T008 [P] Create backend .env.example with required variables in `backend/.env.example`
- [x] T009 [P] Create frontend .env.example with required variables in `frontend/.env.example`
- [x] T010 [P] Configure ruff linting for backend in `backend/pyproject.toml`
- [x] T011 [P] Configure ESLint for frontend in `frontend/.eslintrc.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T012 Create environment configuration loader in `backend/src/config.py`
- [x] T013 Setup database connection with async SQLModel in `backend/src/database.py`
- [x] T014 [P] Initialize Alembic for migrations in `backend/alembic/`
- [x] T015 Create base error response schema in `backend/src/schemas/error.py`
- [x] T016 [P] Implement global exception handler in `backend/src/main.py`
- [x] T017 [P] Create JWT utility functions (create, verify) in `backend/src/utils/security.py`
- [x] T018 [P] Create password hashing utilities (bcrypt) in `backend/src/utils/security.py`
- [x] T019 Create FastAPI app entry point with CORS in `backend/src/main.py`
- [x] T020 [P] Create TypeScript types from data-model.md in `frontend/src/types/index.ts`
- [x] T021 [P] Create API client base with fetch wrapper in `frontend/src/lib/api.ts`
- [x] T022 [P] Create root layout with Tailwind in `frontend/src/app/layout.tsx`
- [x] T023 Create auth dependency for protected routes in `backend/src/api/deps.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration & Login (Priority: P1)

**Goal**: Allow users to create accounts and login to securely manage their todo list

**Independent Test**: Create account with email/password, login, verify session persists across browser refresh

### Backend Implementation (US1)

- [x] T024 [P] [US1] Create User SQLModel entity in `backend/src/models/user.py`
- [x] T025 [P] [US1] Create User Pydantic schemas (UserCreate, UserLogin, UserResponse, AuthResponse) in `backend/src/schemas/user.py`
- [x] T026 [US1] Create initial Alembic migration for users table in `backend/alembic/versions/001_users.py`
- [x] T027 [US1] Implement AuthService (register, login, logout, get_current_user) in `backend/src/services/auth.py`
- [x] T028 [US1] Implement POST /api/v1/auth/register endpoint in `backend/src/api/auth.py`
- [x] T029 [US1] Implement POST /api/v1/auth/login endpoint in `backend/src/api/auth.py`
- [x] T030 [US1] Implement POST /api/v1/auth/logout endpoint in `backend/src/api/auth.py`
- [x] T031 [US1] Implement GET /api/v1/auth/me endpoint in `backend/src/api/auth.py`
- [x] T032 [US1] Register auth router in FastAPI app in `backend/src/main.py`

### Frontend Implementation (US1)

- [x] T033 [P] [US1] Configure Better Auth client in `frontend/src/lib/auth.ts`
- [x] T034 [P] [US1] Create auth context/provider for session state in `frontend/src/lib/auth-provider.tsx`
- [x] T035 [US1] Create registration form component in `frontend/src/components/auth/register-form.tsx`
- [x] T036 [US1] Create login form component in `frontend/src/components/auth/login-form.tsx`
- [x] T037 [US1] Create register page in `frontend/src/app/(auth)/register/page.tsx`
- [x] T038 [US1] Create login page in `frontend/src/app/(auth)/login/page.tsx`
- [x] T039 [US1] Create landing page with login/register links in `frontend/src/app/page.tsx`
- [x] T040 [US1] Implement logout functionality in header component in `frontend/src/components/ui/header.tsx`
- [x] T041 [US1] Add protected route middleware in `frontend/src/middleware.ts`

**Checkpoint**: User Story 1 complete - users can register, login, logout, and sessions persist

---

## Phase 4: User Story 2 - Web-Based Todo Management (Priority: P2)

**Goal**: Allow logged-in users to manage todos via web interface with CRUD operations

**Independent Test**: After login, add a task, view list, update, toggle, delete. All persist across refresh.

### Backend Implementation (US2)

- [x] T042 [P] [US2] Create Task SQLModel entity in `backend/src/models/task.py`
- [x] T043 [P] [US2] Create Task Pydantic schemas (TaskCreate, TaskUpdate, TaskResponse, TaskListResponse) in `backend/src/schemas/task.py`
- [x] T044 [US2] Create Alembic migration for tasks table in `backend/alembic/versions/002_tasks.py`
- [x] T045 [US2] Implement TaskService (create, list, get, update, delete, toggle) in `backend/src/services/task.py`
- [x] T046 [US2] Implement GET /api/v1/tasks endpoint (list with pagination) in `backend/src/api/tasks.py`
- [x] T047 [US2] Implement POST /api/v1/tasks endpoint in `backend/src/api/tasks.py`
- [x] T048 [US2] Implement GET /api/v1/tasks/{id} endpoint in `backend/src/api/tasks.py`
- [x] T049 [US2] Implement PUT /api/v1/tasks/{id} endpoint in `backend/src/api/tasks.py`
- [x] T050 [US2] Implement DELETE /api/v1/tasks/{id} endpoint in `backend/src/api/tasks.py`
- [x] T051 [US2] Implement PATCH /api/v1/tasks/{id}/toggle endpoint in `backend/src/api/tasks.py`
- [x] T052 [US2] Register tasks router in FastAPI app in `backend/src/main.py`

### Frontend Implementation (US2)

- [x] T053 [P] [US2] Create task list component in `frontend/src/components/tasks/task-list.tsx`
- [x] T054 [P] [US2] Create task item component in `frontend/src/components/tasks/task-item.tsx`
- [x] T055 [P] [US2] Create task form component (add/edit) in `frontend/src/components/tasks/task-form.tsx`
- [x] T056 [US2] Create tasks API client functions in `frontend/src/lib/api.ts`
- [x] T057 [US2] Create tasks dashboard page in `frontend/src/app/(dashboard)/tasks/page.tsx`
- [x] T058 [US2] Implement add task functionality with optimistic UI in `frontend/src/components/tasks/task-form.tsx`
- [x] T059 [US2] Implement toggle completion with visual indicator in `frontend/src/components/tasks/task-item.tsx`
- [x] T060 [US2] Implement delete task with confirmation in `frontend/src/components/tasks/task-item.tsx`
- [x] T061 [US2] Implement edit task inline or modal in `frontend/src/components/tasks/task-item.tsx`
- [x] T062 [US2] Add responsive design for mobile in `frontend/src/components/tasks/task-list.tsx`

**Checkpoint**: User Story 2 complete - full CRUD operations work via web UI

---

## Phase 5: User Story 3 - RESTful API Access (Priority: P3)

**Goal**: Provide well-defined API endpoints with proper documentation and versioning

**Independent Test**: Make authenticated API calls to each endpoint, verify responses and status codes

### Implementation (US3)

- [x] T063 [US3] Configure OpenAPI/Swagger documentation in `backend/src/main.py`
- [x] T064 [US3] Add API versioning with /api/v1/ prefix in `backend/src/main.py`
- [x] T065 [P] [US3] Document all endpoints with OpenAPI descriptions in `backend/src/api/auth.py`
- [x] T066 [P] [US3] Document all endpoints with OpenAPI descriptions in `backend/src/api/tasks.py`
- [x] T067 [US3] Ensure consistent error response format across all endpoints in `backend/src/schemas/error.py`
- [x] T068 [US3] Add request/response examples to OpenAPI docs in `backend/src/schemas/`

**Checkpoint**: User Story 3 complete - API is fully documented and versioned

---

## Phase 6: User Story 4 - Data Persistence (Priority: P4)

**Goal**: Ensure tasks are stored permanently and accessible across sessions/devices

**Independent Test**: Create tasks, close browser, reopen on different device, verify tasks present

### Implementation (US4)

- [x] T069 [US4] Add database indexes for performance in `backend/alembic/versions/003_indexes.py`
- [x] T070 [US4] Implement pagination in task list endpoint in `backend/src/services/task.py`
- [x] T071 [US4] Add database connection pooling configuration in `backend/src/database.py`
- [x] T072 [US4] Implement graceful database error handling in `backend/src/main.py`
- [x] T073 [US4] Add loading state for task list in frontend in `frontend/src/components/tasks/task-list.tsx`
- [x] T074 [US4] Add error state for database failures in frontend in `frontend/src/components/ui/error-message.tsx`

**Checkpoint**: User Story 4 complete - data persists reliably across sessions

---

## Phase 7: User Story 5 - Secure Data Access (Priority: P5)

**Goal**: Ensure users can only access their own tasks

**Independent Test**: Login as User A, create tasks, login as User B, verify A's tasks not visible

### Implementation (US5)

- [x] T075 [US5] Ensure all task queries filter by user_id in `backend/src/services/task.py`
- [x] T076 [US5] Add ownership check before task update/delete in `backend/src/services/task.py`
- [x] T077 [US5] Return 403 Forbidden for unauthorized task access in `backend/src/api/tasks.py`
- [x] T078 [US5] Configure CORS to allow only frontend origin in `backend/src/main.py`
- [x] T079 [P] [US5] Add security headers middleware in `backend/src/main.py`
- [x] T080 [US5] Verify password hashing uses bcrypt in `backend/src/utils/security.py`

**Checkpoint**: User Story 5 complete - data isolation verified

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements across all user stories

- [x] T081 [P] Verify responsive design on mobile viewports in `frontend/src/`
- [x] T082 [P] Add loading spinners for async operations in `frontend/src/components/ui/loading.tsx`
- [x] T083 [P] Add success/error toast notifications in `frontend/src/components/ui/toast.tsx`
- [x] T084 Run ruff linting and fix issues in `backend/src/`
- [x] T085 [P] Run ESLint and fix issues in `frontend/src/`
- [x] T086 [P] Run mypy type checking in `backend/src/`
- [x] T087 [P] Verify TypeScript strict mode passes in `frontend/src/`
- [x] T088 Validate quickstart.md setup instructions work end-to-end
- [x] T089 Update README with project setup and usage

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
┌───────────────────────────────────────────────────┐
│  Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3)   │
│       ↓              ↓              ↓             │
│  Phase 6 (US4) and Phase 7 (US5) can run after   │
│  US1+US2 are complete                             │
└───────────────────────────────────────────────────┘
    ↓
Phase 8 (Polish)
```

### User Story Dependencies

- **US1 (Auth)**: Required first - all other stories need authentication
- **US2 (CRUD)**: Depends on US1 - needs authenticated user for task ownership
- **US3 (API)**: Can run in parallel with US2 - documentation enhancement
- **US4 (Persistence)**: Depends on US2 - adds pagination and reliability
- **US5 (Security)**: Depends on US1+US2 - hardens existing implementation

### Within Each User Story

1. Backend models before services
2. Services before API endpoints
3. Backend complete before frontend integration
4. Core functionality before polish

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# Run in parallel:
T002, T003 (backend init)
T004, T005, T006, T007 (frontend init)
T008, T009 (env files)
T010, T011 (linting)
```

**Phase 2 (Foundational)**:
```bash
# Run in parallel:
T014, T015, T16 (backend infrastructure)
T017, T018 (security utilities)
T020, T021, T022 (frontend infrastructure)
```

**Phase 3 (US1)**:
```bash
# Backend models in parallel:
T024, T025

# Frontend components in parallel:
T033, T034
```

**Phase 4 (US2)**:
```bash
# Backend models in parallel:
T042, T043

# Frontend components in parallel:
T053, T054, T055
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T023)
3. Complete Phase 3: User Story 1 (T024-T041)
4. **STOP and VALIDATE**: Users can register and login
5. Demo MVP capability

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Auth) → Users can register/login (MVP!)
3. Add US2 (CRUD) → Full task management
4. Add US3 (API Docs) → Developer-friendly API
5. Add US4 (Persistence) → Reliable storage
6. Add US5 (Security) → Production-ready security
7. Polish → Final cleanup

---

## Summary

| Phase | User Story | Tasks | Parallel Tasks |
|-------|------------|-------|----------------|
| 1 | Setup | 11 | 10 |
| 2 | Foundational | 12 | 8 |
| 3 | US1 - Auth | 18 | 6 |
| 4 | US2 - CRUD | 21 | 5 |
| 5 | US3 - API | 6 | 2 |
| 6 | US4 - Persistence | 6 | 0 |
| 7 | US5 - Security | 6 | 1 |
| 8 | Polish | 9 | 7 |
| **Total** | | **89** | **39** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend uses `backend/src/` prefix, frontend uses `frontend/src/` prefix
