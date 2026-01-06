# Implementation Plan: AI-Powered Chat MCP Server

**Branch**: `003-chat-mcp-server` | **Date**: 2026-01-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-chat-mcp-server/spec.md`

## Summary

Implement an AI-powered chatbot that enables natural language task management using Model Context Protocol (MCP) for tool standardization and OpenAI Agents SDK for AI reasoning. The architecture follows a stateless pattern where conversation state is persisted to PostgreSQL and loaded per request, ensuring reliability and scalability.

**Hackathon Differentiation Strategy**:
1. **MCP-First Architecture**: Standardized tool protocol enables future AI provider switching
2. **Graceful Degradation**: MockAgent ensures system works without API key (demo-friendly)
3. **Stateless Design**: Database-backed conversations enable horizontal scaling
4. **Quick Actions**: UX optimization reduces friction for common operations

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, MCP >= 1.25.0, OpenAI SDK >= 2.14.0
- Frontend: Next.js 16+, Tailwind CSS
**Storage**: PostgreSQL via Neon (conversations, messages, tasks, users)
**Testing**: pytest (backend), Jest/Playwright (frontend)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- Chat response < 5 seconds (with AI)
- Fallback response < 2 seconds (MockAgent)
- Concurrent users: 100+ (stateless design)
**Constraints**:
- OpenAI API rate limits (free tier: 3 RPM, 200 RPD)
- Stateless endpoints (no server-side session storage)
- JWT authentication required for all chat operations
**Scale/Scope**: Phase 3 hackathon feature, building on Phase 2 infrastructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Spec-Driven | Feature has spec.md | ✅ PASS | specs/003-chat-mcp-server/spec.md created |
| II. Python Best Practices | PEP 8, type hints, docstrings | ✅ PASS | Enforced via ruff linting |
| III. Simplicity First | Phase III dependencies approved | ✅ PASS | MCP, OpenAI approved in constitution v3.0.0 |
| IV. Modular Architecture | Separate models/services/API | ✅ PASS | Conversation model, ConversationService, chat API |
| V. Type Safety | All functions typed | ✅ PASS | Full type hints on all new code |
| VI. Test-Driven | Testable, injectable deps | ✅ PASS | MockAgent enables testing without API |
| VII. API-First | OpenAPI, stateless, JWT | ✅ PASS | Chat endpoints documented, JWT auth |
| VIII. Full-Stack Standards | Next.js patterns, TypeScript | ✅ PASS | Client component for interactivity |
| IX. AI Integration | MCP, graceful degradation | ✅ PASS | Core architecture follows this principle |

**Gate Result**: ✅ ALL PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/003-chat-mcp-server/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: MCP patterns, OpenAI best practices
├── data-model.md        # Phase 1: Conversation/Message entities
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: Chat API contracts
│   └── chat.yaml        # OpenAPI spec for chat endpoints
├── checklists/
│   └── requirements.md  # Spec quality validation
└── tasks.md             # Phase 2: Implementation tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── conversation.py    # Conversation, Message SQLModel entities
│   ├── services/
│   │   └── conversation.py    # ConversationService for state management
│   ├── api/
│   │   └── chat.py            # Chat API endpoints
│   ├── agents/
│   │   ├── __init__.py
│   │   └── todo_agent.py      # TodoAgent (OpenAI) + MockTodoAgent
│   ├── schemas/
│   │   └── chat.py            # Pydantic schemas for chat
│   └── config.py              # OpenAI API key configuration
├── mcp_server.py              # Standalone MCP server (5 tools)
├── alembic/versions/
│   └── 004_conversations.py   # Migration for conversations/messages
└── tests/
    ├── unit/
    │   └── test_conversation_service.py
    └── integration/
        └── test_chat_api.py

frontend/
├── src/
│   ├── app/
│   │   └── chat/
│   │       └── page.tsx       # Chat page with auth
│   ├── components/
│   │   └── chat/
│   │       └── chat-container.tsx  # Main chat UI component
│   ├── lib/
│   │   └── chat-api.ts        # Chat API client functions
│   └── types/
│       └── index.ts           # Chat-related TypeScript types
└── tests/
    └── e2e/
        └── chat.spec.ts       # E2E chat flow tests
```

**Structure Decision**: Web application structure (Option 2) - extends existing Phase 2 frontend/backend split with new chat-specific modules.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                          │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────────────┐│
│  │ Chat Page   │  │ ChatContainer   │  │ Quick Action Buttons     ││
│  │ /chat       │→ │ Messages List   │  │ "Show tasks" "Add task"  ││
│  └─────────────┘  │ Input Box       │  └──────────────────────────┘│
│                   └────────┬────────┘                               │
└────────────────────────────┼────────────────────────────────────────┘
                             │ POST /api/chat
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      Chat API Endpoint                          ││
│  │  1. Verify JWT token                                            ││
│  │  2. Load/create conversation from DB                            ││
│  │  3. Run TodoAgent with user message                             ││
│  │  4. Persist assistant response                                  ││
│  │  5. Return response + tool calls                                ││
│  └─────────────────────────────┬───────────────────────────────────┘│
│                                │                                    │
│  ┌─────────────────────────────▼───────────────────────────────────┐│
│  │                       TodoAgent                                  ││
│  │  ┌─────────────────┐    ┌─────────────────┐                     ││
│  │  │ OpenAI Client   │ OR │ MockTodoAgent   │ (fallback)          ││
│  │  │ gpt-4o-mini     │    │ Pattern matcher │                     ││
│  │  └────────┬────────┘    └─────────────────┘                     ││
│  │           │ MCP Protocol (stdio)                                 ││
│  │           ▼                                                      ││
│  │  ┌─────────────────────────────────────────────────────────────┐││
│  │  │                    MCP Server (subprocess)                   │││
│  │  │  Tools: add_task, list_tasks, complete_task,                │││
│  │  │         delete_task, update_task                            │││
│  │  │  DB: Sync PostgreSQL connection (separate from FastAPI)     │││
│  │  └─────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                      PostgreSQL (Neon)                          ││
│  │  Tables: users, tasks, sessions, conversations, messages        ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Stateless Chat Endpoint

**Decision**: Load conversation from DB per request, persist after response.

**Rationale**:
- Enables horizontal scaling (any server can handle any request)
- Simplifies deployment (no sticky sessions)
- Matches constitution principle VII (stateless backend)

**Trade-off**: Slightly higher latency (DB read per request) vs. session-based approach.

### 2. MCP Server as Subprocess

**Decision**: Run MCP server as separate Python process with stdio communication.

**Rationale**:
- Standard MCP protocol for tool exposure
- Clean separation between AI agent and tool implementation
- Enables future swapping of MCP servers

**Trade-off**: Process spawn overhead (~100ms) vs. in-process function calls.

### 3. MockTodoAgent Fallback

**Decision**: Provide pattern-matching fallback when OpenAI unavailable.

**Rationale**:
- Demo-friendly (works without API key)
- Graceful degradation per constitution IX
- Enables testing without external dependencies

**Trade-off**: Limited NLU capabilities vs. full AI reasoning.

### 4. UUID-based IDs

**Decision**: Use UUID for Conversation and Message IDs.

**Rationale**:
- Consistent with existing Task/User models
- No sequential enumeration vulnerability
- Works with distributed systems

## Hackathon Competitive Advantages

### Out-of-Box Features for Maximum Points

| Feature | Points Impact | Implementation Status |
|---------|---------------|----------------------|
| MCP Tool Protocol | High (innovation) | ✅ Implemented |
| Natural Language Task CRUD | High (core feature) | ✅ Implemented |
| Conversation Persistence | Medium (UX) | ✅ Implemented |
| Quick Action Buttons | Medium (UX) | ✅ Implemented |
| Graceful Degradation | High (reliability) | ✅ Implemented |
| JWT Authentication | Required | ✅ Implemented |

### Differentiators vs. Other Submissions

1. **MCP Standard**: Most submissions will use direct function calls; MCP shows industry awareness
2. **Stateless Architecture**: Demonstrates production-ready thinking
3. **Fallback Agent**: Shows reliability engineering mindset
4. **Tool Call Transparency**: UI shows which tools were called (debugging UX)

## Complexity Tracking

> No constitution violations requiring justification.

| Decision | Why This Approach | Simpler Alternative | Why Rejected |
|----------|-------------------|---------------------|--------------|
| MCP subprocess | Standard protocol | Direct function calls | Loses MCP points, less extensible |
| Separate Message entity | Query flexibility | JSON in Conversation | Can't query messages individually |
| Custom chat UI | Full control | ChatKit library | Domain restrictions, less customizable |

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI rate limits (3 RPM free tier) | High | MockAgent fallback, queue requests |
| MCP server crash | Medium | Error handling, restart subprocess |
| Long AI response time | Medium | 30s timeout, loading UI |
| Database unavailable | High | Proper error messages, no crash |

## Next Steps

1. **Run `/sp.tasks`**: Generate implementation tasks from this plan
2. **Verify Implementation**: Compare existing code against spec requirements
3. **Add OpenAI API Key**: Configure OPENAI_API_KEY in backend/.env
4. **Run Migration**: Apply 004_conversations.py migration
5. **Test End-to-End**: Verify chat flow with real OpenAI API

---

**Plan Status**: ✅ Complete - Ready for `/sp.tasks`
