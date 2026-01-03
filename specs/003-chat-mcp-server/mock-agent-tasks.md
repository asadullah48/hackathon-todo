# Tasks: MockTodoAgent Enhancement

**Input**: Design documents from `/specs/003-chat-mcp-server/`
**Prerequisites**: mock-agent-plan.md, mock-agent-spec.md, mock-agent-research.md, mock-agent-data-model.md, contracts/mock-agent.yaml

**Tests**: Not explicitly requested - minimal tests included for pattern matching validation only.

**Organization**: Tasks grouped by user story for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/agents/todo_agent.py` (main file to modify)
- **Tests**: `backend/tests/test_mock_agent.py` (optional)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare MockTodoAgent class structure

- [x] T001 Add import statements for `re` module in backend/src/agents/todo_agent.py
- [x] T002 Define COMMAND_PATTERNS dict with regex patterns in backend/src/agents/todo_agent.py
- [x] T003 Define CommandType type alias (Literal['add', 'list', 'complete', 'delete', 'update', 'unknown']) in backend/src/agents/todo_agent.py
- [x] T004 Define ParsedCommand dataclass with fields (command_type, task_title, task_id, status_filter, new_title) in backend/src/agents/todo_agent.py

---

## Phase 2: Foundational (Command Parser)

**Purpose**: Core pattern matching logic that all user stories depend on

**CRITICAL**: No user story work can begin until command parser is complete

- [x] T005 Implement `_parse_command()` method in MockTodoAgent to detect command type from message in backend/src/agents/todo_agent.py
- [x] T006 Implement `_extract_task_title()` helper to get title from add commands in backend/src/agents/todo_agent.py
- [x] T007 Implement `_extract_uuid()` helper to extract UUID from complete/delete/update commands in backend/src/agents/todo_agent.py
- [x] T008 Implement `_detect_status_filter()` helper to detect all/pending/completed from list commands in backend/src/agents/todo_agent.py
- [x] T009 Implement `_get_help_message()` method returning usage instructions in backend/src/agents/todo_agent.py

**Checkpoint**: Command parser ready - user story implementation can begin

---

## Phase 3: User Story 1 - Add Tasks via Natural Language (Priority: P1)

**Goal**: Users can add tasks by typing "Add buy groceries" or similar

**Independent Test**: Type "Add buy groceries" → task created with title "buy groceries"

### Implementation for User Story 1

- [x] T010 [US1] Add `_connect_mcp()` async context manager method reusing TodoAgent's pattern in backend/src/agents/todo_agent.py
- [x] T011 [US1] Add `_call_add_task()` method to invoke add_task MCP tool in backend/src/agents/todo_agent.py
- [x] T012 [US1] Update `run()` method to handle 'add' command type - parse title and call MCP in backend/src/agents/todo_agent.py
- [x] T013 [US1] Build ToolCallInfo for add_task with arguments and result in backend/src/agents/todo_agent.py
- [x] T014 [US1] Format response with "[Demo Mode]" prefix for add operations in backend/src/agents/todo_agent.py

**Checkpoint**: User Story 1 (Add Tasks) is fully functional

---

## Phase 4: User Story 2 - List Tasks via Natural Language (Priority: P1)

**Goal**: Users can list tasks by typing "Show my tasks" or "What's pending?"

**Independent Test**: Type "Show my tasks" → formatted list of all tasks appears

### Implementation for User Story 2

- [x] T015 [US2] Add `_call_list_tasks()` method to invoke list_tasks MCP tool with status filter in backend/src/agents/todo_agent.py
- [x] T016 [US2] Update `run()` method to handle 'list' command type - detect filter and call MCP in backend/src/agents/todo_agent.py
- [x] T017 [US2] Build ToolCallInfo for list_tasks with arguments and result in backend/src/agents/todo_agent.py
- [x] T018 [US2] Format response with "[Demo Mode]" prefix for list operations in backend/src/agents/todo_agent.py

**Checkpoint**: User Stories 1 AND 2 (Add + List) are fully functional

---

## Phase 5: User Story 3 - Complete Tasks via Natural Language (Priority: P2)

**Goal**: Users can mark tasks complete by typing "Complete task [UUID]"

**Independent Test**: Type "Complete task abc-123..." with valid UUID → task marked complete

### Implementation for User Story 3

- [x] T019 [US3] Add `_call_complete_task()` method to invoke complete_task MCP tool in backend/src/agents/todo_agent.py
- [x] T020 [US3] Update `run()` method to handle 'complete' command type - extract UUID and call MCP in backend/src/agents/todo_agent.py
- [x] T021 [US3] Handle missing UUID case - return guidance to list tasks first in backend/src/agents/todo_agent.py
- [x] T022 [US3] Build ToolCallInfo for complete_task with arguments and result in backend/src/agents/todo_agent.py

**Checkpoint**: User Stories 1, 2, AND 3 (Add + List + Complete) are fully functional

---

## Phase 6: User Story 4 - Delete Tasks via Natural Language (Priority: P2)

**Goal**: Users can delete tasks by typing "Delete task [UUID]"

**Independent Test**: Type "Delete task abc-123..." with valid UUID → task removed

### Implementation for User Story 4

- [x] T023 [US4] Add `_call_delete_task()` method to invoke delete_task MCP tool in backend/src/agents/todo_agent.py
- [x] T024 [US4] Update `run()` method to handle 'delete' command type - extract UUID and call MCP in backend/src/agents/todo_agent.py
- [x] T025 [US4] Handle missing UUID case - return guidance to list tasks first in backend/src/agents/todo_agent.py
- [x] T026 [US4] Build ToolCallInfo for delete_task with arguments and result in backend/src/agents/todo_agent.py

**Checkpoint**: User Stories 1-4 (Add + List + Complete + Delete) are fully functional

---

## Phase 7: User Story 5 - Update Tasks via Natural Language (Priority: P3)

**Goal**: Users can update task title by typing "Update task [UUID] to 'new title'"

**Independent Test**: Type "Update abc-123... to 'Buy fruits'" → task title updated

### Implementation for User Story 5

- [x] T027 [US5] Add `_call_update_task()` method to invoke update_task MCP tool in backend/src/agents/todo_agent.py
- [x] T028 [US5] Implement `_extract_new_title()` helper to get new title from update commands in backend/src/agents/todo_agent.py
- [x] T029 [US5] Update `run()` method to handle 'update' command type - extract UUID + new title and call MCP in backend/src/agents/todo_agent.py
- [x] T030 [US5] Handle missing UUID or title case - return guidance message in backend/src/agents/todo_agent.py
- [x] T031 [US5] Build ToolCallInfo for update_task with arguments and result in backend/src/agents/todo_agent.py

**Checkpoint**: All 5 user stories (Add + List + Complete + Delete + Update) are fully functional

---

## Phase 8: Edge Cases & Error Handling

**Purpose**: Handle edge cases from spec

- [x] T032 Handle empty message input - return prompt for command in backend/src/agents/todo_agent.py
- [x] T033 Handle unrecognized command - return help message with examples in backend/src/agents/todo_agent.py
- [x] T034 Handle MCP connection failure - wrap in try/except, return graceful error message in backend/src/agents/todo_agent.py
- [x] T035 Handle MCP tool errors - pass through error text to user in backend/src/agents/todo_agent.py

---

## Phase 9: Polish & Validation

**Purpose**: Final cleanup and verification

- [x] T036 Add docstrings to all new methods following PEP 257 in backend/src/agents/todo_agent.py
- [x] T037 Add type hints to all new methods per constitution V in backend/src/agents/todo_agent.py
- [x] T038 Run linting check: `uv run ruff check backend/src/agents/todo_agent.py`
- [x] T039 Manual test: verify MockTodoAgent is selected when OPENAI_API_KEY is not set
- [x] T040 Manual test: run all 5 command types through chat endpoint
- [x] T041 Verify tool_calls array is populated for each operation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Add) and US2 (List) are P1 priority
  - US3 (Complete) and US4 (Delete) are P2 priority
  - US5 (Update) is P3 priority
- **Edge Cases (Phase 8)**: Can run after core stories or in parallel
- **Polish (Phase 9)**: Depends on all phases complete

### User Story Dependencies

- **User Story 1 (Add)**: Depends only on Foundational - No other story dependencies
- **User Story 2 (List)**: Depends only on Foundational - No other story dependencies
- **User Story 3 (Complete)**: Depends only on Foundational - Logically uses List to find UUIDs
- **User Story 4 (Delete)**: Depends only on Foundational - Logically uses List to find UUIDs
- **User Story 5 (Update)**: Depends only on Foundational - Logically uses List to find UUIDs

### Within Each User Story

- MCP call method first
- Update run() method to handle command type
- Handle edge cases
- Build ToolCallInfo

### Parallel Opportunities

Since all changes are in a single file (todo_agent.py), parallel execution is limited:

- T001-T004 (Setup) are sequential (same file)
- T005-T009 (Foundational) are sequential (same file)
- User stories must be implemented sequentially (same run() method)
- Edge cases and polish can follow any order

---

## Parallel Example: None (Single File)

Since all tasks modify `backend/src/agents/todo_agent.py`, parallelization is not possible.

Execute sequentially: Setup → Foundational → US1 → US2 → US3 → US4 → US5 → Edge Cases → Polish

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T009)
3. Complete Phase 3: User Story 1 - Add (T010-T014)
4. Complete Phase 4: User Story 2 - List (T015-T018)
5. **STOP and VALIDATE**: Test "Add buy groceries" and "Show my tasks"
6. Deploy/demo if ready - users can add and view tasks!

### Incremental Delivery

1. MVP (Add + List) → Users can manage basic task creation
2. + Complete (US3) → Users can mark tasks done
3. + Delete (US4) → Users can remove tasks
4. + Update (US5) → Full CRUD operations
5. + Edge Cases → Production-ready error handling
6. + Polish → Clean code ready for review

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | T001-T004 | Imports, patterns, types |
| Foundational | T005-T009 | Command parser |
| US1 (Add) | T010-T014 | Add task functionality |
| US2 (List) | T015-T018 | List tasks functionality |
| US3 (Complete) | T019-T022 | Complete task functionality |
| US4 (Delete) | T023-T026 | Delete task functionality |
| US5 (Update) | T027-T031 | Update task functionality |
| Edge Cases | T032-T035 | Error handling |
| Polish | T036-T041 | Cleanup and validation |

**Total Tasks**: 41
**MVP Scope**: T001-T018 (18 tasks)
**Estimated LOC**: ~150-200 lines added to todo_agent.py

---

## Notes

- All tasks modify single file: `backend/src/agents/todo_agent.py`
- Regex patterns from research.md RQ2
- MCP connection pattern from TodoAgent (lines 124-134)
- Response format: "[Demo Mode] " + MCP result
- Commit after each phase for easy rollback
