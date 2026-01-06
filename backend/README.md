---
title: Hackathon Todo Backend
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
---

# Hackathon Todo Backend

FastAPI backend for todo application with JWT authentication.

## Features
- User authentication (JWT)
- Task CRUD operations
- PostgreSQL database (Neon)
- RESTful API

## Endpoints
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
