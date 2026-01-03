# Research: MockTodoAgent Enhancement

**Date**: 2026-01-03
**Feature**: MockTodoAgent Pattern-Based Command Parsing
**Related Spec**: [mock-agent-spec.md](./mock-agent-spec.md)

## Research Questions

### RQ1: Best Pattern Matching Approach for NLP Commands

**Question**: What is the most effective pattern matching approach for parsing natural language todo commands without AI?

**Research**:

| Approach | Pros | Cons |
|----------|------|------|
| Simple keyword search | Fast, easy to implement | Miss variations, order-dependent |
| Regex with groups | Flexible, extract arguments | Complex patterns needed |
| Word tokenization | Language-aware | Overkill for simple commands |
| Fuzzy matching | Handles typos | Adds dependency (fuzzywuzzy) |

**Decision**: **Regex with named groups**

**Rationale**:
- Standard library (no new dependencies per Constitution III)
- Can extract task titles and IDs in single match
- Case-insensitive matching handles variations
- Well-tested approach for command parsing

**Alternatives Rejected**:
- Fuzzy matching: Would require external dependency
- NLP tokenization: Overkill, adds complexity
- Simple keyword search: Can't extract arguments reliably

---

### RQ2: Regex Patterns for Todo Commands

**Question**: What regex patterns effectively capture natural language todo commands?

**Research**: Analyzed common phrasings from spec acceptance scenarios:

| Command | Sample Inputs | Pattern Components |
|---------|---------------|-------------------|
| Add | "Add buy groceries", "Create task to call mom", "Remember to pay bills", "I need to finish report" | Trigger words + capture remaining text |
| List | "Show my tasks", "What's pending?", "List completed", "Display todos" | Trigger words + optional status filter |
| Complete | "Complete task abc-123", "Mark abc-123 done", "Finish task abc-123" | Trigger words + UUID capture |
| Delete | "Delete task abc-123", "Remove abc-123" | Trigger words + UUID capture |
| Update | "Update abc-123 to 'new title'", "Change task abc-123 title to something" | Trigger words + UUID + new title capture |

**Decision**: Use the following patterns:

```python
PATTERNS = {
    'add': re.compile(
        r'(?:add|create|remember|need\s+to|have\s+to)\s+(?:a\s+)?(?:task\s+(?:to\s+)?)?(.+)',
        re.IGNORECASE
    ),
    'list': re.compile(
        r'(?:show|list|what|display|get|see).*?(?:tasks?|todos?|pending|completed|done)',
        re.IGNORECASE
    ),
    'complete': re.compile(
        r'(?:complete|done|finish|mark).*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        re.IGNORECASE
    ),
    'delete': re.compile(
        r'(?:delete|remove|cancel).*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        re.IGNORECASE
    ),
    'update': re.compile(
        r'(?:update|change|rename|modify).*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*?(?:to|title|name)\s+["\']?(.+?)["\']?\s*$',
        re.IGNORECASE
    ),
}
```

**UUID Pattern**: Standard UUID v4 format `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`

---

### RQ3: Status Filter Detection for List Command

**Question**: How to detect status filters (all, pending, completed) in list commands?

**Research**: Analyzed filter variations:

| User Says | Detected Filter |
|-----------|----------------|
| "Show my tasks" | all |
| "What's pending?" | pending |
| "Show pending tasks" | pending |
| "List completed" | completed |
| "What have I done?" | completed |
| "What's left?" | pending |

**Decision**: Secondary regex check after list command detected:

```python
def detect_status_filter(message: str) -> str:
    message_lower = message.lower()
    if any(word in message_lower for word in ['pending', 'left', 'remaining', 'todo', 'incomplete']):
        return 'pending'
    if any(word in message_lower for word in ['completed', 'done', 'finished']):
        return 'completed'
    return 'all'
```

---

### RQ4: MCP Client Connection Pattern

**Question**: How should MockTodoAgent connect to MCP server?

**Research**: Analyzed existing TodoAgent implementation:

```python
# TodoAgent pattern (lines 124-134 of todo_agent.py)
server_params = StdioServerParameters(
    command="python",
    args=[self.mcp_server_path],
    env={**os.environ},
)

async with (
    stdio_client(server_params) as (read, write),
    ClientSession(read, write) as mcp_session,
):
    await mcp_session.initialize()
    # ... use session
```

**Decision**: Reuse identical pattern in MockTodoAgent

**Rationale**:
- Proven to work
- Same MCP server, same protocol
- Maintains consistency

---

### RQ5: Error Handling Strategy

**Question**: How to handle various failure modes gracefully?

**Research**: Identified failure scenarios:

| Scenario | Detection | Response |
|----------|-----------|----------|
| No command recognized | No pattern matches | Help message with examples |
| MCP server unavailable | Connection exception | "Service temporarily unavailable" |
| Task not found | MCP returns error text | Pass through error to user |
| Empty message | Empty string after strip | Prompt for command |
| UUID not found in message | Pattern matches but no UUID | Suggest listing tasks first |

**Decision**: Layered error handling:

1. Input validation (empty check)
2. Pattern matching (return help if no match)
3. MCP connection (try/except with graceful message)
4. Tool execution (pass through MCP errors)

---

### RQ6: Response Message Formatting

**Question**: How to format responses for consistency with AI agent?

**Research**: Analyzed TodoAgent response style from MCP server output:

```text
# From add_task_handler:
"Task created successfully!\n- ID: {task.id}\n- Title: {task.title}"

# From list_tasks_handler:
"Found {len(tasks)} task(s):\n{formatted_list}"

# From complete_task_handler:
"Task completed! ✓ '{task.title}'"
```

**Decision**: Use MCP server responses directly, add "Demo Mode" prefix for MockAgent:

```python
def format_response(mcp_result: str, is_mock: bool = True) -> str:
    prefix = "[Demo Mode] " if is_mock else ""
    return f"{prefix}{mcp_result}"
```

---

## Summary of Decisions

| Topic | Decision | Justification |
|-------|----------|---------------|
| Pattern matching | Regex with named groups | Standard library, flexible extraction |
| UUID detection | Standard UUID v4 regex | Strict validation prevents errors |
| Status filter | Keyword-based secondary check | Simple, covers common variations |
| MCP connection | Reuse TodoAgent pattern | Proven, consistent |
| Error handling | Layered with graceful fallbacks | User-friendly, spec-compliant |
| Response format | MCP output + Demo Mode prefix | Transparency, consistency |

## Implementation Ready

All research questions resolved. Ready for Phase 1: Design & Contracts.
