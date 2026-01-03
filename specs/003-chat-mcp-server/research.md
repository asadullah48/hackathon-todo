# Research: AI-Powered Chat MCP Server

**Feature**: 003-chat-mcp-server
**Date**: 2026-01-03
**Purpose**: Resolve technical unknowns and document best practices for Phase 3 implementation

## Research Topics

### 1. MCP (Model Context Protocol) Integration

**Question**: How to properly implement MCP server for AI agent tool exposure?

**Decision**: Standalone Python MCP server with stdio transport

**Rationale**:
- MCP >= 1.25.0 provides `FastMCP` class for easy server creation
- stdio transport is the standard for subprocess communication
- Each tool is a decorated function that returns structured results

**Implementation Pattern**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("todo-server")

@mcp.tool()
def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Add a new task for the user."""
    # Implementation with database access
    return {"success": True, "task_id": "..."}
```

**Alternatives Considered**:
- HTTP transport: More complex, unnecessary for single-host deployment
- SSE transport: Streaming not needed for our use case
- Direct function calls: Loses MCP standardization benefits

---

### 2. OpenAI Agents SDK Integration

**Question**: How to connect OpenAI to MCP tools?

**Decision**: Use `openai` SDK with function calling and MCP stdio client

**Rationale**:
- OpenAI SDK >= 2.14.0 supports native function/tool calling
- `mcp` library provides `stdio_client` for subprocess communication
- Tools are dynamically loaded from MCP server's `list_tools()` response

**Implementation Pattern**:
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

async def run_agent(user_message: str, user_id: str):
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env={"USER_ID": user_id}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            # Convert to OpenAI format and call chat completions
```

**Alternatives Considered**:
- LangChain: Heavy dependency, unnecessary abstraction
- Custom agent loop: More work, less maintainable
- Claude API: Would require Anthropic SDK, we chose OpenAI

---

### 3. Stateless Conversation Management

**Question**: How to persist and load conversation state efficiently?

**Decision**: Database-backed conversations with per-request loading

**Rationale**:
- SQLModel provides async database access
- Conversation and Message entities enable efficient queries
- Loading full conversation for context is acceptable (messages are small)

**Implementation Pattern**:
```python
class ConversationService:
    async def get_or_create_conversation(
        self, user_id: UUID, conversation_id: UUID | None
    ) -> Conversation:
        if conversation_id:
            return await self._get_conversation(conversation_id)
        return await self._create_conversation(user_id)

    async def add_message(
        self, conversation_id: UUID, role: str, content: str
    ) -> Message:
        # Persist message to database
```

**Alternatives Considered**:
- Redis session: Adds infrastructure complexity
- In-memory cache: Not persistent, loses state on restart
- Cookie-based: Security concerns with message content

---

### 4. Graceful Degradation Pattern

**Question**: How to handle missing/unavailable AI provider?

**Decision**: MockTodoAgent with pattern-matching fallback

**Rationale**:
- Enables demo without API key configuration
- Provides predictable responses for common commands
- Follows constitution IX requirement for graceful degradation

**Implementation Pattern**:
```python
class MockTodoAgent:
    PATTERNS = {
        r"add.*task.*['\"](.+?)['\"]": "add_task",
        r"show.*tasks?|list.*tasks?": "list_tasks",
        r"complete.*['\"](.+?)['\"]": "complete_task",
    }

    async def run(self, message: str, user_id: str) -> str:
        for pattern, action in self.PATTERNS.items():
            if match := re.search(pattern, message, re.I):
                return await self._execute_action(action, match, user_id)
        return "I can help with: adding tasks, listing tasks, completing tasks..."
```

**Alternatives Considered**:
- Error message only: Poor UX, fails demo scenarios
- Disable chat feature: Breaks feature entirely
- Local LLM: High resource requirements, complex setup

---

### 5. Frontend Chat UI Design

**Question**: Build custom UI or use ChatKit library?

**Decision**: Custom ChatContainer component

**Rationale**:
- ChatKit requires domain allowlisting (per phase guide)
- Custom UI provides full control over styling and behavior
- Simpler integration with existing Next.js/Tailwind stack

**Implementation Pattern**:
```typescript
export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    // POST to /api/chat
    // Update messages state
  };

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      <QuickActions onAction={handleQuickAction} />
      <ChatInput value={input} onChange={setInput} onSend={sendMessage} />
    </div>
  );
}
```

**Alternatives Considered**:
- ChatKit: Domain restrictions, less customizable
- React Chat Widget: Not TypeScript native
- Build from scratch: More work than needed

---

### 6. OpenAI Free Tier Limitations

**Question**: How to work within free tier rate limits?

**Decision**: Design for 3 RPM limit with graceful handling

**Rationale**:
- Free tier: 3 requests per minute, 200 per day
- MockAgent absorbs overflow
- UI should show rate limit messages gracefully

**Mitigation Strategies**:
1. Use MockAgent for testing/demo
2. Show "AI is busy, please wait" message
3. Queue requests client-side (debounce rapid typing)
4. Consider caching common responses

**Rate Limit Response Pattern**:
```python
except openai.RateLimitError:
    return {
        "response": "AI is currently busy. Using fallback mode.",
        "tool_calls": [],
        "used_fallback": True
    }
```

---

## Research Summary

| Topic | Decision | Confidence |
|-------|----------|------------|
| MCP Integration | FastMCP with stdio | High |
| OpenAI SDK | Direct SDK with function calling | High |
| Conversation State | Database-backed, per-request load | High |
| Graceful Degradation | MockTodoAgent pattern matching | High |
| Chat UI | Custom ChatContainer | High |
| Rate Limits | MockAgent fallback + graceful messages | Medium |

## Unresolved Questions

None - all technical unknowns have been resolved through research.

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [SQLModel Async](https://sqlmodel.tiangolo.com/tutorial/async/)
- [Next.js App Router](https://nextjs.org/docs/app)
