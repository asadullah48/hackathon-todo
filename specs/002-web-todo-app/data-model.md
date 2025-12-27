# Data Model: Full-Stack Web Todo Application

**Feature**: 002-web-todo-app | **Date**: 2025-12-28 | **Phase**: 1 (Design)

## Overview

This document defines the data model for the Full-Stack Web Todo Application. All models use SQLModel for database persistence with Pydantic for API validation.

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│                User                 │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ email: str (unique, indexed)        │
│ hashed_password: str                │
│ created_at: datetime                │
│ updated_at: datetime                │
└──────────────────┬──────────────────┘
                   │
                   │ 1:N
                   │
                   ▼
┌─────────────────────────────────────┐
│                Task                 │
├─────────────────────────────────────┤
│ id: UUID (PK)                       │
│ user_id: UUID (FK → User.id)        │
│ title: str (1-200 chars)            │
│ description: str | None (0-1000)    │
│ is_completed: bool (default: False) │
│ created_at: datetime                │
│ updated_at: datetime                │
└─────────────────────────────────────┘
```

## Entity Definitions

### User

Represents a registered account holder in the system.

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class User(SQLModel, table=True):
    """User entity for authentication and task ownership."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- `email` must be unique and valid email format
- `hashed_password` stores bcrypt hash, never plaintext
- `id` is auto-generated UUID for distributed safety

**Indexes**:
- Primary key on `id`
- Unique index on `email` for fast login lookup

---

### Task

Represents a todo item belonging to a specific user.

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field
from typing import Optional

class Task(SQLModel, table=True):
    """Task entity for todo items."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- `user_id` must reference valid User
- `title` required, 1-200 characters
- `description` optional, 0-1000 characters
- `is_completed` defaults to False

**Indexes**:
- Primary key on `id`
- Index on `user_id` for user-scoped queries
- Consider composite index on `(user_id, created_at)` for sorted lists

---

## Pydantic Schemas (API DTOs)

### User Schemas

```python
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

# Request schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str  # Plain password, will be hashed

class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str

# Response schemas
class UserResponse(BaseModel):
    """Schema for user in API responses."""
    id: UUID
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
```

### Task Schemas

```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# Request schemas
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)

# Response schemas
class TaskResponse(BaseModel):
    """Schema for task in API responses."""
    id: UUID
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Schema for paginated task list."""
    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int
```

---

## Database Schema (SQL)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Validation Rules

### User Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| email | Valid email format | "Invalid email format" |
| email | Unique in database | "Email already registered" |
| password | Min 8 characters | "Password must be at least 8 characters" |

### Task Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required, not empty | "Title is required" |
| title | Max 200 characters | "Title must be 200 characters or less" |
| description | Max 1000 characters | "Description must be 1000 characters or less" |

---

## Data Lifecycle

### User Lifecycle
1. **Created**: On registration with email/password
2. **Active**: Can create/manage tasks
3. **Deleted**: Cascade deletes all associated tasks

### Task Lifecycle
1. **Created**: New task with `is_completed=False`
2. **Updated**: Title/description modified, `updated_at` refreshed
3. **Toggled**: `is_completed` flipped, `updated_at` refreshed
4. **Deleted**: Permanently removed from database

---

## Migration Strategy

Using SQLModel with Alembic for migrations:

```python
# alembic/versions/001_initial.py
"""Initial migration - users and tasks tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(), primary_key=True),
        sa.Column('user_id', postgresql.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_created', 'tasks', ['user_id', 'created_at'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('users')
```

---

## TypeScript Types (Frontend)

```typescript
// types/index.ts

export interface User {
  id: string;
  email: string;
  createdAt: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  isCompleted: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface TaskCreateInput {
  title: string;
  description?: string;
}

export interface TaskUpdateInput {
  title?: string;
  description?: string;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string>;
}
```
