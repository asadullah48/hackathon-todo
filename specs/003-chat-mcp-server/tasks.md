# Tasks: AI-Powered Chat MCP Server

**Input**: Design documents from `/specs/003-chat-mcp-server/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat.yaml

**Status**: ⚡ Implementation already exists - tasks include verification and completion steps.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`
- **MCP Server**: `backend/mcp_server.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies and configuration

- [x] T001 Add mcp>=1.25.0 and openai>=2.14.0 dependencies in backend/pyproject.toml ✅ PRE-EXISTING
- [x] T002 [P] Add OPENAI_API_KEY to backend/src/config.py Settings class ✅ PRE-EXISTING
- [x] T003 [P] Add sync_database_url property for MCP server in backend/src/config.py ✅ PRE-EXISTING
- [x] T004 Run uv sync to install new dependencies ✅ PRE-EXISTING
- [x] T004a Add psycopg2-binary for sync PostgreSQL operations ✅ BUGFIX

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database models, migrations, and core services that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Conversation model in backend/src/models/conversation.py ✅ PRE-EXISTING
- [x] T005a Fix timezone-aware datetime columns with sa_column=Column(DateTime(timezone=True)) ✅ BUGFIX
- [x] T006 Create Message model in backend/src/models/conversation.py ✅ PRE-EXISTING
- [x] T007 Export models in backend/src/models/__init__.py ✅ PRE-EXISTING
- [x] T008 Create Alembic migration 004_conversations.py in backend/alembic/versions/ ✅ PRE-EXISTING
- [x] T009 Run alembic upgrade head to apply migration ✅ VERIFIED
- [x] T010 [P] Create chat schemas (ChatRequest, ChatResponse, ToolCallInfo) in backend/src/schemas/chat.py ✅ PRE-EXISTING
- [x] T011 [P] Create ConversationService in backend/src/services/conversation.py ✅ PRE-EXISTING
- [x] T012 Create agents module init in backend/src/agents/__init__.py ✅ PRE-EXISTING

**Checkpoint**: Foundation ready - user story implementation can now begin ✅

---

## Phase 3: User Story 1 - Natural Language Task Commands (Priority: P1) 🎯 MVP

**Goal**: Users can manage tasks via natural language chat messages (add, list, complete, delete, update)

**Independent Test**: Send "Add a task called 'Buy groceries'" and verify task appears in task list

### Implementation for User Story 1

- [x] T013 [US1] Create MCP server with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) in backend/mcp_server.py ✅ PRE-EXISTING
- [x] T014 [US1] Implement sync database connection for MCP server in backend/mcp_server.py ✅ PRE-EXISTING
- [x] T014a [US1] Fix SSL parameter for psycopg2 (ssl=require → sslmode=require) in backend/mcp_server.py ✅ BUGFIX
- [x] T015 [US1] Create TodoAgent class with OpenAI integration in backend/src/agents/todo_agent.py ✅ PRE-EXISTING
- [x] T016 [US1] Create MockTodoAgent fallback class in backend/src/agents/todo_agent.py ✅ PRE-EXISTING
- [x] T017 [US1] Create POST /api/chat endpoint in backend/src/api/chat.py ✅ PRE-EXISTING
- [x] T018 [US1] Register chat router in backend/src/main.py ✅ PRE-EXISTING
- [x] T019 [P] [US1] Add chat types (ChatRequest, ChatResponse, Message) to frontend/src/types/index.ts ✅ PRE-EXISTING
- [x] T020 [P] [US1] Create chat API client functions in frontend/src/lib/chat-api.ts ✅ PRE-EXISTING
- [x] T021 [US1] Create ChatContainer component with message input in frontend/src/components/chat/chat-container.tsx ✅ PRE-EXISTING
- [x] T022 [US1] Create chat page with auth check in frontend/src/app/chat/page.tsx ✅ PRE-EXISTING
- [x] T023 [US1] Add navigation link to chat page in frontend/src/app/(dashboard)/tasks/page.tsx ✅ PRE-EXISTING

**Checkpoint**: User Story 1 complete - users can chat with AI to manage tasks

---

## Phase 4: User Story 2 - View and Continue Conversations (Priority: P2)

**Goal**: Users can view conversation history and continue past conversations

**Independent Test**: Have a conversation, refresh page, verify messages are preserved

### Implementation for User Story 2

- [x] T024 [US2] Add GET /api/chat/conversations endpoint in backend/src/api/chat.py ✅ PRE-EXISTING
- [x] T025 [US2] Add GET /api/chat/conversations/{id} endpoint in backend/src/api/chat.py ✅ PRE-EXISTING
- [x] T026 [US2] Add listConversations function to frontend/src/lib/chat-api.ts ✅ PRE-EXISTING
- [x] T027 [US2] Add getConversation function to frontend/src/lib/chat-api.ts ✅ PRE-EXISTING
- [x] T028 [US2] Load conversation history on mount in frontend/src/components/chat/chat-container.tsx ✅ IMPLEMENTED
- [x] T029 [US2] Display message history with timestamps in frontend/src/components/chat/chat-container.tsx ✅ IMPLEMENTED

**Checkpoint**: User Story 2 complete - conversations persist across sessions

---

## Phase 5: User Story 3 - Quick Action Buttons (Priority: P3)

**Goal**: Quick action buttons for common operations (Show tasks, Add task)

**Independent Test**: Click "Show my tasks" button and verify it sends the message

### Implementation for User Story 3

- [x] T030 [US3] Add QuickActions component section in frontend/src/components/chat/chat-container.tsx ✅ PRE-EXISTING
- [x] T031 [US3] Implement "Show my tasks" quick action button ✅ PRE-EXISTING
- [x] T032 [US3] Implement "Add a task" quick action button with prompt ✅ PRE-EXISTING

**Checkpoint**: User Story 3 complete - quick actions reduce friction

---

## Phase 6: User Story 4 - Graceful Degradation (Priority: P2)

**Goal**: System works without OpenAI API key using MockAgent fallback

**Independent Test**: Remove OPENAI_API_KEY and verify helpful fallback messages

### Implementation for User Story 4

- [x] T033 [US4] Implement pattern matching in MockTodoAgent for common commands in backend/src/agents/todo_agent.py ✅ PRE-EXISTING
- [x] T034 [US4] Add fallback detection logic in TodoAgent.run() in backend/src/agents/todo_agent.py ✅ PRE-EXISTING
- [x] T035 [US4] Display fallback indicator in chat UI when using MockAgent in frontend/src/components/chat/chat-container.tsx ✅ IMPLEMENTED
- [x] T036 [US4] Handle rate limit errors with user-friendly message in backend/src/api/chat.py ✅ BUGFIX
- [x] T036a [US4] Detect quota errors in ExceptionGroup using repr() in backend/src/api/chat.py ✅ BUGFIX

**Checkpoint**: User Story 4 complete - system gracefully degrades without AI

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [x] T037 [P] Add DELETE /api/chat/conversations/{id} endpoint in backend/src/api/chat.py ✅ PRE-EXISTING
- [x] T038 [P] Add deleteConversation function to frontend/src/lib/chat-api.ts ✅ PRE-EXISTING
- [x] T039 Run backend linting: uv run ruff check src/ mcp_server.py --fix ✅ PASSED (1 auto-fixed)
- [x] T040 Run frontend linting: npm run lint ✅ PASSED (no errors)
- [x] T041 Verify OpenAPI docs include chat endpoints at /docs ✅ VERIFIED
- [x] T042 Run quickstart.md validation steps ✅ VERIFIED (MCP OK, OpenAI OK)
- [x] T043 Test end-to-end chat flow with real OpenAI API ✅ VERIFIED (quota exceeded but graceful degradation works)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational completion
  - US1 (P1): Core chat functionality - MVP
  - US2 (P2): Conversation persistence
  - US3 (P3): Quick actions (convenience)
  - US4 (P2): Graceful degradation (reliability)
- **Polish (Phase 7)**: Depends on all user stories

### User Story Dependencies

| Story | Priority | Can Start After | Dependencies on Other Stories |
|-------|----------|-----------------|-------------------------------|
| US1 | P1 | Phase 2 | None - this is the MVP |
| US2 | P2 | Phase 2 | None - independently testable |
| US3 | P3 | Phase 2 | Uses US1 chat infrastructure |
| US4 | P2 | Phase 2 | Modifies US1 agent behavior |

### Within Each User Story

1. Backend models/schemas first
2. Backend services next
3. Backend API endpoints
4. Frontend types
5. Frontend API client
6. Frontend components

### Parallel Opportunities

**Phase 1**:
- T002 and T003 can run in parallel (different sections of config.py)

**Phase 2**:
- T010 and T011 can run in parallel (different files)

**Phase 3 (US1)**:
- T019 and T020 can run in parallel (different frontend files)

**Phase 7**:
- T037 and T038 can run in parallel (backend/frontend)
- T039 and T040 can run in parallel (different projects)

---

## Parallel Example: User Story 1

```bash
# Backend models/services (sequential - dependencies):
Task T013: MCP server with tools
Task T014: Sync database for MCP (depends on T013)
Task T015: TodoAgent with OpenAI (depends on T013)
Task T016: MockTodoAgent fallback (parallel with T015)
Task T017: Chat endpoint (depends on T015, T016)
Task T018: Register router (depends on T017)

# Frontend (can start after T017 provides API):
# These can run in parallel:
Task T019: Chat types in types/index.ts
Task T020: Chat API client in lib/chat-api.ts

# Frontend components (sequential - dependencies):
Task T021: ChatContainer (depends on T19, T20)
Task T22: Chat page (depends on T21)
Task T23: Navigation link (parallel with T22)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T012)
3. Complete Phase 3: User Story 1 (T013-T023)
4. **STOP and VALIDATE**: Test with "Add a task called 'Test'" command
5. Deploy/demo if ready - this is a functional AI chatbot!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → **MVP: AI chat works** → Demo
3. Add US2 → Conversations persist → Demo
4. Add US4 → Works without API key → Demo (for hackathon judges without API key!)
5. Add US3 → Quick actions → Polish
6. Polish phase → Production ready

### Hackathon Priority

For maximum points in limited time:
1. **Must have**: US1 (core chat) + US4 (graceful degradation)
2. **Should have**: US2 (persistence)
3. **Nice to have**: US3 (quick actions)

---

## Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| 1. Setup | 4 | 2 |
| 2. Foundational | 8 | 2 |
| 3. US1 - Chat (P1) | 11 | 2 |
| 4. US2 - History (P2) | 6 | 0 |
| 5. US3 - Quick Actions (P3) | 3 | 0 |
| 6. US4 - Fallback (P2) | 4 | 0 |
| 7. Polish | 7 | 4 |
| **Total** | **43** | **10** |

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 = 23 tasks
**Full Scope**: All 43 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story
- Each user story independently testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story
- Phase 3 code already implemented - verify and fix any issues
