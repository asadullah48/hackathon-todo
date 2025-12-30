# Panaversity Hackathon II: Spec-Driven Todo Application

## 🎯 Project Overview

A comprehensive todo application built using specification-driven development methodology, progressing through 5 phases from CLI to cloud-native AI-powered system.

## 👨‍💻 Developer Information

- **Name:** Asadullah Shafique
- **GitHub:** [@asadullah48](https://github.com/asadullah48)
- **Hackathon:** Panaversity Hackathon II - Spec-Driven Development

## 🚀 Live Demo

- **Frontend:** https://hackathon-todo-frontend-chi.vercel.app
- **Backend:** Running locally (FastAPI)
- **Database:** Neon PostgreSQL (Cloud)

## ✅ Completed Phases

### Phase 1: CLI Todo Application ✅
- Python-based command-line interface
- Basic CRUD operations
- Local data persistence
- Built with SpecifyKit SDK

### Phase 2: Web Application ✅
- **Backend:** FastAPI with JWT authentication
- **Frontend:** Next.js 15 with TypeScript
- **Database:** PostgreSQL (Neon)
- **Features:**
  - User registration & login
  - JWT-based authentication
  - Task CRUD operations
  - User isolation
  - Responsive UI with Tailwind CSS
- **Deployed:** Vercel (Frontend)

### Phase 3: MCP + AI Chatbot 🚧 (In Progress)
Coming tomorrow: AI-powered todo management with MCP server and OpenAI Agents SDK

## 🛠️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- JWT Authentication
- Alembic (migrations)
- UV (package manager)

### Frontend
- Next.js 15
- TypeScript
- React 19
- Tailwind CSS
- Better Auth

### Infrastructure
- Vercel (Frontend deployment)
- Neon (PostgreSQL database)
- Docker (containerization)

## 📁 Project Structure
```
hackathon-todo/
├── backend/          # FastAPI backend
│   ├── src/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   └── main.py   # Application entry
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/         # Next.js frontend
│   ├── src/
│   │   ├── app/      # App router pages
│   │   ├── components/
│   │   └── lib/      # Auth & utilities
│   └── package.json
├── .specify/         # SpecifyKit Plus workflow
│   ├── memory/
│   ├── scripts/
│   └── templates/
└── .claude/          # Claude AI skills
    └── skills/
        └── hackathon-todo-advanced/
```

## 🎯 Methodology: Spec-Driven Development

Following Panaversity's SpecifyKit Plus methodology:

1. **Constitution:** `.specify/memory/constitution.md`
   - All code generated from specifications
   - No manual coding without prior spec
   - Strict adherence to PEP 8, type hints

2. **Workflow:**
   - Specification → Plan → Tasks → Implementation
   - Using `.specify/scripts/bash/` workflow scripts
   - Template-driven development

3. **Documentation:**
   - Comprehensive phase guides
   - MCP server setup instructions
   - Kubernetes deployment specs

## 📚 Key Features Implemented

### Authentication
- [x] User registration
- [x] JWT token-based login
- [x] Password hashing (bcrypt)
- [x] Protected routes
- [x] Token refresh

### Task Management
- [x] Create tasks
- [x] Read tasks (user-isolated)
- [x] Update tasks
- [x] Delete tasks
- [x] Mark tasks as complete

### User Experience
- [x] Responsive design
- [x] Form validation
- [x] Error handling
- [x] Loading states
- [x] Logout functionality

## 🧪 Testing

### Local Testing
```bash
# Backend
cd backend
uv run uvicorn src.main:app --reload

# Frontend
cd frontend
npm run dev
```

### API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Current user
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/toggle` - Toggle completion

## 📝 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=...
CORS_ORIGINS=...
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=...
DATABASE_URL=...
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Local Development)
```bash
cd backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 📊 Database Schema

### Users Table
- id (UUID, primary key)
- email (unique)
- name
- password_hash
- created_at
- updated_at

### Tasks Table
- id (UUID, primary key)
- title
- description
- completed (boolean)
- user_id (foreign key)
- created_at
- updated_at

## 🎓 Learning Outcomes

1. Spec-driven development methodology
2. Full-stack application architecture
3. JWT authentication implementation
4. Database design with user isolation
5. Cloud deployment strategies
6. Docker containerization
7. Modern Python async patterns
8. Next.js App Router & Server Components

## 🔄 Next Steps (Phase 3-5)

- [ ] Phase 3: MCP Server + OpenAI Agents + ChatKit
- [ ] Phase 4: Kubernetes with Minikube
- [ ] Phase 5: Cloud deployment with Dapr & Kafka

## 📄 License

MIT License

## 🙏 Acknowledgments

- Panaversity for the hackathon framework
- SpecifyKit Plus methodology
- Claude AI for development assistance

---

**Status:** Phase 2 Complete | Phase 3 In Progress  
**Last Updated:** December 30, 2024  
**Submission Date:** TBD
