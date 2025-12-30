# Hackathon Todo

A full-stack todo application with both CLI and web interfaces.

## Features

### Phase I: CLI Application
- Add new tasks with title and optional description
- View all tasks with status indicators
- Update task title and description
- Delete tasks
- Toggle task completion status

### Phase II: Web Application
- User registration and authentication
- Responsive web interface
- RESTful API with OpenAPI documentation
- Persistent database storage
- Secure data isolation between users

## Project Structure

```
hackathon-todo/
├── backend/                 # FastAPI REST API
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # SQLModel entities
│   │   ├── schemas/        # Pydantic DTOs
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
│
├── frontend/               # Next.js web app
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── tests/             # Frontend tests
│
├── src/                    # Phase I CLI app
└── specs/                  # Feature specifications
```

## Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env
# Edit .env with your database URL and secrets

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn src.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

### API Documentation

Once the backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Backend

```bash
cd backend

# Run tests
uv run pytest

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/
```

### Frontend

```bash
cd frontend

# Run linting
npm run lint

# Run type check
npm run type-check

# Run tests
npm test
```

### CLI (Phase I)

```bash
# Run CLI
uv run todo

# Run tests
uv run pytest
```

## Tech Stack

### Backend
- Python 3.12+
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- PostgreSQL (Neon)
- JWT authentication

### Frontend
- Next.js 15+
- TypeScript
- Tailwind CSS
- React 19

## Environment Variables

### Backend (.env)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `CORS_ORIGINS` - Allowed frontend origins

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL

## 🎉 Phase 2 Status: COMPLETE ✅

### Live Demo
- **Frontend**: [Your Vercel URL] (deploy when ready)
- **Backend**: [Your Backend URL] (deploy when ready)

### Features Implemented
- ✅ User registration and authentication
- ✅ JWT-based session management
- ✅ Task CRUD operations (Create, Read, Update, Delete)
- ✅ Mark tasks as complete/incomplete
- ✅ User isolation (users only see their own tasks)
- ✅ Persistent storage with PostgreSQL
- ✅ Responsive UI with Tailwind CSS

### Tech Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, SQLModel, PostgreSQL (Neon)
- **Auth**: JWT tokens, password hashing (bcrypt)
- **Deployment**: Ready for Vercel (frontend) + Railway/Render (backend)

---

## 📚 Phase 3: Coming Next

Phase 3 will add AI capabilities:
- MCP (Model Context Protocol) server
- OpenAI Agents SDK integration
- ChatKit interface for conversational task management
- AI-powered task suggestions

**Phase 3 guides available in:** `docs/phase-guides/`

