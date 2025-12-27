# Quickstart Guide: Full-Stack Web Todo Application

**Feature**: 002-web-todo-app | **Date**: 2025-12-28

## Overview

This guide walks you through setting up and running the Full-Stack Web Todo Application locally for development.

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 20+ | Frontend runtime |
| Python | 3.12+ | Backend runtime |
| UV | Latest | Python package manager |
| Git | Latest | Version control |

### Required Accounts (for deployment)

- **Neon**: Free PostgreSQL database - [neon.tech](https://neon.tech)
- **Vercel**: Frontend hosting - [vercel.com](https://vercel.com)
- **Render/Railway**: Backend hosting - [render.com](https://render.com) or [railway.app](https://railway.app)

## Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd hackathon-todo

# Checkout feature branch
git checkout 002-web-todo-app
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment and install dependencies
uv sync

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# DATABASE_URL=postgresql+asyncpg://user:pass@host/db
# JWT_SECRET=your-secret-key-here
# CORS_ORIGINS=http://localhost:3000
```

### 3. Database Setup

```bash
# Create Neon database at https://neon.tech
# Copy connection string to .env as DATABASE_URL

# Run migrations
uv run alembic upgrade head
```

### 4. Start Backend

```bash
# Start FastAPI server (default: http://localhost:8000)
uv run uvicorn src.main:app --reload

# Verify: open http://localhost:8000/docs for API docs
```

### 5. Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with your settings
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
# BETTER_AUTH_SECRET=your-auth-secret-here
```

### 6. Start Frontend

```bash
# Start Next.js dev server (default: http://localhost:3000)
npm run dev

# Open http://localhost:3000 in your browser
```

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Security
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Auth
BETTER_AUTH_SECRET=your-better-auth-secret-key

# Environment
NODE_ENV=development
```

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
uv run pytest                    # All tests
uv run pytest tests/unit         # Unit tests only
uv run pytest tests/integration  # Integration tests only
uv run pytest --cov=src          # With coverage

# Frontend tests
cd frontend
npm test                         # All tests
npm run test:watch               # Watch mode
npm run test:coverage            # With coverage
```

### Linting & Formatting

```bash
# Backend
cd backend
uv run ruff check src tests      # Lint
uv run ruff format src tests     # Format
uv run mypy src                  # Type check

# Frontend
cd frontend
npm run lint                     # ESLint
npm run lint:fix                 # Auto-fix
npm run type-check               # TypeScript check
```

### Database Migrations

```bash
cd backend

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one version
uv run alembic downgrade -1

# View current version
uv run alembic current
```

## API Documentation

Once the backend is running, access interactive API docs at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Deployment

### Backend (Render)

1. Create new Web Service on Render
2. Connect GitHub repository
3. Set build command: `pip install uv && uv sync`
4. Set start command: `uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

### Frontend (Vercel)

1. Import project from GitHub
2. Framework preset: Next.js
3. Add environment variables from `.env.local`
4. Deploy

### Database (Neon)

1. Create project at neon.tech
2. Create database
3. Copy connection string (with `?sslmode=require`)
4. Add to backend environment as `DATABASE_URL`

## Project Structure

```
hackathon-todo/
├── backend/
│   ├── src/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Environment config
│   │   ├── database.py       # Database connection
│   │   ├── models/           # SQLModel entities
│   │   ├── schemas/          # Pydantic DTOs
│   │   ├── services/         # Business logic
│   │   ├── api/              # API endpoints
│   │   └── utils/            # Utilities
│   ├── tests/
│   ├── alembic/              # Migrations
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities
│   │   └── types/            # TypeScript types
│   ├── tests/
│   └── package.json
│
└── specs/
    └── 002-web-todo-app/     # This feature's docs
```

## Common Issues

### CORS Errors

**Problem**: Browser blocks API requests with CORS error.

**Solution**: Ensure `CORS_ORIGINS` in backend `.env` includes your frontend URL (e.g., `http://localhost:3000`).

### Database Connection Failed

**Problem**: Backend can't connect to Neon database.

**Solution**:
1. Check `DATABASE_URL` format includes `+asyncpg`
2. Ensure `?sslmode=require` is appended for Neon
3. Verify IP allowlist in Neon dashboard

### JWT Token Invalid

**Problem**: API returns 401 on authenticated requests.

**Solution**:
1. Check `JWT_SECRET` matches in backend config
2. Verify token isn't expired (7-day default)
3. Ensure `Authorization: Bearer <token>` header format

### Better Auth Session Issues

**Problem**: Frontend loses authentication on refresh.

**Solution**:
1. Verify `BETTER_AUTH_SECRET` is set
2. Check browser cookies are enabled
3. Ensure same-site cookie settings match deployment

## Next Steps

After completing setup:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement backend API endpoints
3. Implement frontend pages and components
4. Run tests and verify all acceptance criteria
5. Deploy to staging environment
