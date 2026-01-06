# Research: Full-Stack Web Todo Application

**Feature**: 002-web-todo-app | **Date**: 2025-12-28 | **Phase**: 0 (Research)

## Overview

This document captures technology research and decisions for transforming the Phase I CLI todo application into a full-stack web application with authentication, persistent storage, and RESTful API.

## Technology Decisions

### 1. Backend Framework: FastAPI

**Decision**: Use FastAPI as the backend REST API framework.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| FastAPI | Async-first, auto OpenAPI docs, Pydantic integration, high performance | Newer ecosystem |
| Flask | Mature, simple, large ecosystem | No async, no built-in validation |
| Django REST | Batteries included, mature ORM | Heavier, opinion-heavy |

**Rationale**: FastAPI is mandated by constitution v2.0.0. It provides automatic OpenAPI documentation (Principle VII), native Pydantic validation, and async support for database operations.

**References**:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- Constitution Principle VII: API-First Design

---

### 2. ORM: SQLModel

**Decision**: Use SQLModel for database models and queries.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| SQLModel | Pydantic + SQLAlchemy hybrid, type-safe, FastAPI integration | Newer, less documentation |
| SQLAlchemy | Mature, flexible, well-documented | Verbose, separate Pydantic schemas |
| Raw SQL | Full control, no abstraction overhead | Maintenance burden, SQL injection risk |

**Rationale**: SQLModel is mandated by constitution v2.0.0. It combines SQLAlchemy's power with Pydantic's validation, reducing boilerplate and ensuring type safety.

**References**:
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- Constitution Phase II Technology Stack

---

### 3. Database: Neon PostgreSQL

**Decision**: Use Neon serverless PostgreSQL as the database.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Neon PostgreSQL | Serverless, auto-scaling, generous free tier, branching | Newer service |
| Supabase | Full backend-as-service, auth included | More opinionated, may conflict with Better Auth |
| Railway PostgreSQL | Simple deployment, integrated hosting | Less features than Neon |
| SQLite | Zero config, embedded | Not suitable for production web apps |

**Rationale**: Neon is mandated by constitution v2.0.0. Serverless PostgreSQL reduces operational overhead, provides automatic scaling, and includes a generous free tier for MVP development.

**Connection Pattern**:
```python
# Use async connection with connection pooling
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"
```

**References**:
- [Neon Documentation](https://neon.tech/docs)
- Constitution Phase II Technology Stack

---

### 4. Frontend Framework: Next.js 16+ with App Router

**Decision**: Use Next.js 16+ with the App Router architecture.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Next.js App Router | Server Components, streaming, layouts, React 19 | Learning curve for App Router |
| Next.js Pages Router | Stable, well-documented | Legacy, less optimal for new projects |
| Remix | Full-stack React, nested routes | Smaller ecosystem |
| Vite + React | Fast dev, simple | No SSR out of box, more manual setup |

**Rationale**: Next.js with App Router is mandated by constitution v2.0.0 Principle VIII. Server Components by default provides better performance, and the App Router offers modern patterns like route groups and layouts.

**Key Patterns**:
- Server Components by default (no 'use client' unless needed)
- Route groups: `(auth)` for login/register, `(dashboard)` for authenticated pages
- Layouts for shared UI (header, sidebar)

**References**:
- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- Constitution Principle VIII: Full-Stack Standards

---

### 5. Authentication: Better Auth + JWT

**Decision**: Use Better Auth for frontend authentication with JWT tokens for API access.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Better Auth | Next.js native, simple API, session management | Newer library |
| NextAuth.js | Mature, many providers | More complex setup, heavier |
| Clerk | Full-featured, UI components | Vendor lock-in, cost at scale |
| Custom JWT | Full control | Security risk, maintenance burden |

**Rationale**: Better Auth is mandated by constitution v2.0.0 Principle VIII. It integrates natively with Next.js and provides simple session management with JWT tokens.

**Authentication Flow**:
1. User registers/logs in via Better Auth on frontend
2. Better Auth issues JWT token (7-day expiry)
3. Frontend sends JWT in `Authorization: Bearer <token>` header
4. Backend validates JWT and extracts user_id
5. All task operations scoped to authenticated user_id

**Token Structure**:
```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "exp": 1735344000,
  "iat": 1734739200
}
```

**References**:
- [Better Auth Documentation](https://www.better-auth.com/)
- Constitution Principle VII: JWT-based authentication

---

### 6. Styling: Tailwind CSS

**Decision**: Use Tailwind CSS for all styling.

**Options Considered**:
| Option | Pros | Cons |
|--------|------|------|
| Tailwind CSS | Utility-first, consistent, responsive built-in | Large class strings |
| CSS Modules | Scoped styles, familiar CSS | More files, less reusable |
| styled-components | JS-based, dynamic | Runtime overhead, SSR complexity |
| Plain CSS | Simple, no build step | Global scope issues, maintainability |

**Rationale**: Tailwind CSS is mandated by constitution v2.0.0 Principle VIII. It provides consistent design tokens, built-in responsive utilities, and works well with Server Components.

**References**:
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- Constitution Principle VIII: Full-Stack Standards

---

### 7. Deployment Strategy

**Decision**: Vercel for frontend, Render/Railway for backend, Neon for database.

**Deployment Architecture**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Vercel    │────▶│   Render    │────▶│    Neon     │
│  (Frontend) │     │  (Backend)  │     │ (PostgreSQL)│
│  Next.js    │     │   FastAPI   │     │  Serverless │
└─────────────┘     └─────────────┘     └─────────────┘
```

**Environment Variables**:
- Frontend: `NEXT_PUBLIC_API_URL`, `BETTER_AUTH_SECRET`
- Backend: `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`

**References**:
- Constitution Phase II Technology Stack: Deployment section

---

## Security Considerations

### Password Handling
- Passwords hashed with bcrypt (cost factor 12)
- Never stored or logged in plaintext
- Minimum 8 characters, validated on frontend and backend

### JWT Security
- Signed with HS256 algorithm
- 7-day expiry (per spec FR-005)
- Stored in httpOnly cookies or localStorage (Better Auth handles this)
- Refresh mechanism: user must re-login after expiry

### Data Isolation
- All database queries include `user_id` filter
- Foreign key constraint: `task.user_id` references `user.id`
- API endpoints validate user owns resource before CRUD

### CORS Configuration
- Backend allows only frontend origin
- Credentials mode enabled for cookie-based auth

---

## Performance Considerations

### Backend
- Async database operations with `asyncpg`
- Connection pooling (min 5, max 20 connections)
- Pagination for task lists (default 50 per page)

### Frontend
- Server Components for initial page load
- Client Components only for interactive elements
- Optimistic UI updates for task operations

### Database
- Indexes on `task.user_id` and `task.created_at`
- UUID primary keys for distributed-safe IDs

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Better Auth learning curve | Medium | Follow official docs, start with email/password only |
| Neon cold starts | Low | Keep-alive queries or upgrade to Pro tier |
| CORS configuration errors | High | Explicit allow-list, test in staging |
| JWT token theft | High | httpOnly cookies, short expiry, secure flag |

---

## Next Steps

1. **Phase 1**: Create data-model.md with SQLModel entity definitions
2. **Phase 1**: Create contracts/ with OpenAPI specifications
3. **Phase 1**: Create quickstart.md with setup instructions
4. **Phase 2**: Generate tasks.md with implementation tasks
