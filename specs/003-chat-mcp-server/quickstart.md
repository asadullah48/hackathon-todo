# Quickstart: AI-Powered Chat MCP Server

**Feature**: 003-chat-mcp-server
**Date**: 2026-01-03
**Purpose**: Get Phase 3 chat feature running locally

## Prerequisites

- Phase 2 complete and working (backend + frontend + database)
- Python 3.12+ with UV package manager
- Node.js 18+ with npm
- PostgreSQL database (Neon or local)
- OpenAI API key (optional - MockAgent works without it)

## Setup Steps

### 1. Install Backend Dependencies

```bash
cd backend
uv sync
```

This installs new Phase 3 dependencies:
- `mcp>=1.25.0` - Model Context Protocol SDK
- `openai>=2.14.0` - OpenAI Python SDK

### 2. Configure OpenAI API Key (Optional)

Add to `backend/.env`:

```bash
# OpenAI Configuration (optional - MockAgent fallback if missing)
OPENAI_API_KEY=sk-your-api-key-here
```

**Without API Key**: The chat will use MockTodoAgent with pattern matching.
**With API Key**: Full AI-powered natural language understanding.

### 3. Run Database Migration

```bash
cd backend
uv run alembic upgrade head
```

This creates:
- `conversations` table
- `messages` table
- Required indexes

### 4. Start Backend Server

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

Verify chat endpoints are available:
- http://localhost:8000/docs → Look for `/api/chat` endpoints

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

Navigate to:
- http://localhost:3000/chat → Chat interface

## Testing the Chat

### Quick Test Commands

Try these messages in the chat:

1. **Add a task**:
   ```
   Add a task called "Test the chat feature"
   ```

2. **List tasks**:
   ```
   Show me my tasks
   ```

3. **Complete a task**:
   ```
   Mark "Test the chat feature" as complete
   ```

4. **Delete a task**:
   ```
   Delete the task "Test the chat feature"
   ```

### Quick Action Buttons

Click the quick action buttons for common operations:
- "Show my tasks" - Lists all your tasks
- "Add a task" - Prompts for task details

### API Testing (curl)

```bash
# Get JWT token first (from login)
TOKEN="your-jwt-token"

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my tasks"}'

# List conversations
curl http://localhost:8000/api/chat/conversations \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### "AI is currently unavailable"

**Cause**: OpenAI API key not set or invalid.
**Solution**:
- Check `OPENAI_API_KEY` in `.env`
- Verify key is valid at https://platform.openai.com
- MockAgent will handle requests until key is configured

### "Rate limit exceeded"

**Cause**: OpenAI free tier limits (3 RPM, 200 RPD).
**Solution**:
- Wait 1 minute before retrying
- System automatically falls back to MockAgent
- Consider upgrading OpenAI plan for production

### "Conversation not found"

**Cause**: Invalid conversation_id or accessing another user's conversation.
**Solution**:
- Start a new conversation (don't pass conversation_id)
- Check you're using the correct JWT token

### MCP Server Errors

**Cause**: MCP server subprocess failed to start.
**Solution**:
```bash
# Test MCP server directly
cd backend
python mcp_server.py
# Should show "MCP Server running..."
```

### Database Migration Failed

**Cause**: Migration already applied or schema conflict.
**Solution**:
```bash
# Check migration status
uv run alembic current

# If needed, downgrade and re-upgrade
uv run alembic downgrade -1
uv run alembic upgrade head
```

## Architecture Verification

Run these checks to verify Phase 3 is properly set up:

```bash
# 1. Backend lint check
cd backend && uv run ruff check src/ mcp_server.py

# 2. Frontend lint check
cd frontend && npm run lint

# 3. Test MCP server imports
cd backend && python -c "from mcp.server.fastmcp import FastMCP; print('MCP OK')"

# 4. Test OpenAI imports
cd backend && python -c "from openai import AsyncOpenAI; print('OpenAI OK')"

# 5. Verify database tables
# Connect to your database and run:
# SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
# Should include: conversations, messages
```

## Development Workflow

1. **Backend changes**: Server auto-reloads with `--reload`
2. **Frontend changes**: Next.js hot module replacement
3. **Database changes**: Create new migration with Alembic
4. **MCP tool changes**: Restart backend (subprocess respawns)

## Next Steps

- [ ] Configure production OpenAI API key
- [ ] Deploy backend with chat endpoints
- [ ] Test E2E chat flow
- [ ] Add monitoring for AI token usage
- [ ] Consider Phase 4 (Kubernetes) deployment
