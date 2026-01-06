# Data Model: AI-Powered Chat MCP Server

**Feature**: 003-chat-mcp-server
**Date**: 2026-01-03
**Source**: Extracted from spec.md Key Entities section

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│    User     │ 1───N │  Conversation   │ 1───N │   Message   │
│  (existing) │       │     (new)       │       │    (new)    │
└─────────────┘       └─────────────────┘       └─────────────┘
       │
       │ 1───N
       ▼
┌─────────────┐
│    Task     │
│  (existing) │
└─────────────┘
```

## Entities

### Conversation (NEW)

Represents a chat session between a user and the AI agent.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique conversation identifier |
| user_id | UUID | FK → users.id, NOT NULL, INDEX | Owner of the conversation |
| created_at | datetime | NOT NULL, default=now() | When conversation started |
| updated_at | datetime | NOT NULL, default=now() | Last activity timestamp |

**Relationships**:
- Belongs to: User (many-to-one)
- Has many: Message (one-to-many, cascade delete)

**Validation Rules**:
- user_id must reference existing user
- Conversations are isolated per user (no cross-user access)

**State Transitions**: None (stateless entity)

---

### Message (NEW)

Individual message within a conversation (user input or AI response).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique message identifier |
| conversation_id | UUID | FK → conversations.id, NOT NULL, INDEX | Parent conversation |
| role | string(20) | NOT NULL, enum: user/assistant/system | Message sender type |
| content | text | NOT NULL, default="" | Message text content |
| tool_calls_json | text | NULLABLE | JSON-encoded tool call info |
| created_at | datetime | NOT NULL, default=now() | Message timestamp |

**Relationships**:
- Belongs to: Conversation (many-to-one)

**Validation Rules**:
- role must be one of: "user", "assistant", "system"
- content can be empty for tool-only responses
- tool_calls_json must be valid JSON if present

**State Transitions**: None (immutable after creation)

---

### User (EXISTING - from Phase 2)

Authenticated user who owns conversations and tasks.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | User identifier |
| email | string | UNIQUE, NOT NULL | Login email |
| ... | ... | ... | Other fields from Phase 2 |

**New Relationships for Phase 3**:
- Has many: Conversation (one-to-many)

---

### Task (EXISTING - from Phase 2)

Todo item that can be managed via chat.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Task identifier |
| user_id | UUID | FK → users.id | Task owner |
| title | string | NOT NULL | Task title |
| description | text | NULLABLE | Task details |
| is_completed | boolean | default=false | Completion status |
| ... | ... | ... | Other fields from Phase 2 |

**Chat Integration**:
- MCP tools operate on this entity
- AI agent receives task data via MCP list_tasks tool
- Modifications via add_task, complete_task, delete_task, update_task

---

## Database Migration

**Migration File**: `backend/alembic/versions/004_conversations.py`

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    tool_calls_json TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
```

---

## Schema Definitions (Pydantic)

### Request Schemas

```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: UUID | None = None

class ConversationListParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
```

### Response Schemas

```python
class ToolCallInfo(BaseModel):
    name: str
    arguments: dict[str, Any]
    result: Any | None = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    message: str
    tool_calls: list[ToolCallInfo] = []
    created_at: datetime

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    tool_calls: list[ToolCallInfo] | None = None
    created_at: datetime

class ConversationResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
```

---

## Data Access Patterns

### Read Patterns

1. **Get user's conversations** (list view):
   ```sql
   SELECT * FROM conversations
   WHERE user_id = :user_id
   ORDER BY updated_at DESC
   LIMIT :limit OFFSET :offset
   ```

2. **Get conversation with messages** (chat view):
   ```sql
   SELECT c.*, m.* FROM conversations c
   LEFT JOIN messages m ON m.conversation_id = c.id
   WHERE c.id = :conversation_id AND c.user_id = :user_id
   ORDER BY m.created_at ASC
   ```

3. **Get message history for AI context**:
   ```sql
   SELECT role, content FROM messages
   WHERE conversation_id = :conversation_id
   ORDER BY created_at ASC
   ```

### Write Patterns

1. **Create conversation**:
   ```sql
   INSERT INTO conversations (user_id) VALUES (:user_id) RETURNING *
   ```

2. **Add message**:
   ```sql
   INSERT INTO messages (conversation_id, role, content, tool_calls_json)
   VALUES (:conversation_id, :role, :content, :tool_calls_json)
   ```

3. **Update conversation timestamp**:
   ```sql
   UPDATE conversations SET updated_at = NOW() WHERE id = :id
   ```

### Delete Patterns

1. **Delete conversation** (cascade deletes messages):
   ```sql
   DELETE FROM conversations WHERE id = :id AND user_id = :user_id
   ```

---

## Data Constraints Summary

| Entity | Constraint | Enforcement |
|--------|------------|-------------|
| Conversation | User isolation | WHERE user_id = :current_user |
| Message | Valid role enum | Application validation |
| Message | Max content length | 10,000 characters (application) |
| Tool calls | Valid JSON | Application validation |
| All | UUID format | Database type + Pydantic |
