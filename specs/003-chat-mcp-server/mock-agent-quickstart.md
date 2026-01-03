# Quickstart: MockTodoAgent Testing

**Date**: 2026-01-03
**Feature**: MockTodoAgent Enhancement

## Prerequisites

1. Backend environment setup
2. PostgreSQL database running (Neon or local)
3. MCP server accessible

## Environment Setup

```bash
cd backend

# Ensure virtual environment is active
source .venv/bin/activate

# Verify dependencies
uv pip list | grep -E "mcp|sqlmodel"
```

## Testing MockTodoAgent

### 1. Unit Test - Command Parser

```python
# Test script: test_mock_agent_parser.py
import asyncio
from src.agents.todo_agent import MockTodoAgent

async def test_parser():
    agent = MockTodoAgent()

    # Test ADD command
    test_cases = [
        ("Add buy groceries", "add", "buy groceries"),
        ("Create a task to call mom", "add", "call mom"),
        ("Remember to pay bills", "add", "pay bills"),
        ("Show my tasks", "list", None),
        ("What's pending?", "list", None),
    ]

    for message, expected_cmd, expected_title in test_cases:
        cmd = agent._parse_command(message)
        print(f"'{message}' -> {cmd.command_type}, title={cmd.task_title}")
        assert cmd.command_type == expected_cmd
        if expected_title:
            assert expected_title in cmd.task_title.lower()

asyncio.run(test_parser())
```

### 2. Integration Test - With MCP Server

```python
# Test script: test_mock_agent_mcp.py
import asyncio
import os

# Ensure OPENAI_API_KEY is NOT set (forces MockAgent)
os.environ.pop('OPENAI_API_KEY', None)

from src.agents.todo_agent import get_agent, MockTodoAgent

async def test_mock_agent_mcp():
    agent = get_agent()
    assert isinstance(agent, MockTodoAgent), "Should be MockTodoAgent when no API key"

    user_id = "test-user-uuid-1234"  # Use real user UUID

    # Test 1: Add task
    response, tool_calls = await agent.run(
        user_id=user_id,
        messages=[{"role": "user", "content": "Add buy groceries"}]
    )
    print(f"ADD Response: {response}")
    print(f"Tool calls: {tool_calls}")
    assert len(tool_calls) > 0, "Should have tool calls"
    assert tool_calls[0].tool_name == "add_task"

    # Test 2: List tasks
    response, tool_calls = await agent.run(
        user_id=user_id,
        messages=[{"role": "user", "content": "Show my tasks"}]
    )
    print(f"LIST Response: {response}")
    assert "task" in response.lower() or "found" in response.lower()

asyncio.run(test_mock_agent_mcp())
```

### 3. API Integration Test

```bash
# Start backend server (without OPENAI_API_KEY)
unset OPENAI_API_KEY
uvicorn src.main:app --reload --port 8000

# In another terminal, test chat endpoint
TOKEN="your-jwt-token"

# Test ADD command
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add buy groceries"}'

# Test LIST command
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```

## Expected Responses

### Add Task

```json
{
  "conversation_id": "uuid",
  "response": "[Demo Mode] Task created successfully!\n- ID: abc-123\n- Title: buy groceries",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {"user_id": "user-uuid", "title": "buy groceries"},
      "result": "Task created successfully!..."
    }
  ]
}
```

### List Tasks

```json
{
  "conversation_id": "uuid",
  "response": "[Demo Mode] Found 3 task(s):\n○ [uuid1] buy groceries\n○ [uuid2] call mom\n✓ [uuid3] finished task",
  "tool_calls": [
    {
      "tool_name": "list_tasks",
      "arguments": {"user_id": "user-uuid", "status": "all"},
      "result": "Found 3 task(s):..."
    }
  ]
}
```

### Unrecognized Command

```json
{
  "conversation_id": "uuid",
  "response": "[Demo Mode] I didn't understand that command. Try:\n- 'Add [task title]' to create a task\n- 'Show my tasks' to see your tasks\n- 'Complete [task-id]' to mark done\n- 'Delete [task-id]' to remove a task",
  "tool_calls": []
}
```

## Verification Checklist

- [ ] MockTodoAgent is used when OPENAI_API_KEY is not set
- [ ] Add command creates task in database
- [ ] List command shows user's tasks
- [ ] Complete command marks task done (requires valid UUID)
- [ ] Delete command removes task (requires valid UUID)
- [ ] Unrecognized commands return help message
- [ ] tool_calls array is populated for successful operations
- [ ] Response includes "[Demo Mode]" prefix
- [ ] Response time is < 2 seconds (no AI latency)

## Troubleshooting

### MockTodoAgent not being used

```python
# Check which agent is selected
from src.agents.todo_agent import get_agent
agent = get_agent()
print(type(agent))  # Should be MockTodoAgent
```

Ensure `OPENAI_API_KEY` is not set in environment.

### MCP connection fails

```bash
# Test MCP server directly
cd backend
python mcp_server.py
# Should start without errors
```

Check `DATABASE_URL` is correctly configured.

### Pattern not matching

Test patterns directly:

```python
import re
pattern = r'(?:add|create|remember|need\s+to)\s+(.+)'
match = re.search(pattern, "Add buy groceries", re.IGNORECASE)
print(match.group(1))  # Should print "buy groceries"
```
