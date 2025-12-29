# Backend - FastAPI Todo API

Backend API for Phase II Todo Application.

## Tech Stack
- FastAPI
- SQLModel
- Neon PostgreSQL
- Better Auth JWT

## Setup
```bash
uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

## API Endpoints
- POST /api/auth/register
- POST /api/auth/login
- GET /api/{user_id}/tasks
- POST /api/{user_id}/tasks
- PUT /api/{user_id}/tasks/{id}
- DELETE /api/{user_id}/tasks/{id}
- PATCH /api/{user_id}/tasks/{id}/complete
