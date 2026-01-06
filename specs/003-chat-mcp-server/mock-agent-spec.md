# Feature Specification: MockTodoAgent Enhancement

**Feature Branch**: `003-chat-mcp-server` (enhancement)
**Created**: 2026-01-03
**Status**: Draft
**Input**: User description: "MockTodoAgent Enhancement - Pattern-based natural language command parsing that calls MCP tools directly without OpenAI. Features: detect keywords (add/show/list/complete/delete/update), extract task titles and IDs from messages, call MCP server via stdio client, return actual tool_calls array showing operations performed, provide helpful response messages. Must work as drop-in replacement when OpenAI API is unavailable. Supports same conversation interface as TodoAgent."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Tasks via Natural Language (Priority: P1)

As a user without OpenAI API access, I want to add tasks by typing natural language commands so that I can manage my todos even when the AI provider is unavailable.

**Why this priority**: Core functionality - adding tasks is the most common operation and demonstrates the pattern-based parsing works.

**Independent Test**: Can be fully tested by typing "Add buy groceries" and verifying a task is created in the database with title "buy groceries".

**Acceptance Scenarios**:

1. **Given** I am logged in and OpenAI is unavailable, **When** I type "Add buy groceries", **Then** a task is created with title "buy groceries" and I see confirmation "Task created: buy groceries"
2. **Given** I am in chat, **When** I type "Create a task to call mom", **Then** a task is created with title "call mom"
3. **Given** I am in chat, **When** I type "Remember to pay bills", **Then** a task is created with title "pay bills"
4. **Given** I am in chat, **When** I type "I need to finish the report", **Then** a task is created with title "finish the report"

---

### User Story 2 - List Tasks via Natural Language (Priority: P1)

As a user, I want to view my tasks by typing natural language queries so that I can see what I need to do.

**Why this priority**: Equally critical - users need to see their tasks to manage them.

**Independent Test**: Can be fully tested by typing "Show my tasks" and verifying all user's tasks are listed.

**Acceptance Scenarios**:

1. **Given** I have tasks, **When** I type "Show my tasks", **Then** I see a formatted list of all my tasks
2. **Given** I have pending tasks, **When** I type "What's pending?", **Then** I see only pending tasks
3. **Given** I have completed tasks, **When** I type "Show completed", **Then** I see only completed tasks
4. **Given** I have no tasks, **When** I type "List tasks", **Then** I see "No tasks found" message

---

### User Story 3 - Complete Tasks via Natural Language (Priority: P2)

As a user, I want to mark tasks as complete by describing them so that I can track my progress.

**Why this priority**: Important for task lifecycle but depends on having tasks first.

**Independent Test**: Can be tested by creating a task, then typing "Complete task [ID]" and verifying status changes.

**Acceptance Scenarios**:

1. **Given** I have a task with ID abc-123, **When** I type "Complete task abc-123", **Then** the task is marked complete
2. **Given** I have a task titled "buy groceries", **When** I type "Mark groceries as done", **Then** the system lists tasks to help find the ID (since pattern matching cannot resolve names to IDs without AI)
3. **Given** I reference an invalid task ID, **When** I type "Complete task invalid-id", **Then** I see "Task not found" error

---

### User Story 4 - Delete Tasks via Natural Language (Priority: P2)

As a user, I want to delete tasks by ID so that I can remove items I no longer need.

**Why this priority**: Secondary operation, less frequent than add/list.

**Independent Test**: Can be tested by creating a task, then typing "Delete task [ID]" and verifying removal.

**Acceptance Scenarios**:

1. **Given** I have a task with ID abc-123, **When** I type "Delete task abc-123", **Then** the task is removed
2. **Given** I type "Remove task xyz", **When** the task doesn't exist, **Then** I see "Task not found" error

---

### User Story 5 - Update Tasks via Natural Language (Priority: P3)

As a user, I want to update task details so that I can modify my todos.

**Why this priority**: Least common operation, lower priority.

**Independent Test**: Can be tested by creating a task, then typing "Update task [ID] title: new title" and verifying change.

**Acceptance Scenarios**:

1. **Given** I have a task with ID abc-123, **When** I type "Update task abc-123 to 'Buy groceries and fruits'", **Then** the task title is updated

---

### Edge Cases

- What happens when user sends message with no recognizable command? -> System responds with helpful usage instructions
- What happens when user says "complete groceries" without task ID? -> System suggests listing tasks first to find ID
- What happens when MCP server is unavailable? -> System returns graceful error message
- What happens when user sends empty message? -> System prompts user to type a command
- What happens when multiple commands in one message? -> System processes only the first recognized command

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: MockTodoAgent MUST parse natural language to detect command intent (add, list, complete, delete, update)
- **FR-002**: MockTodoAgent MUST call MCP tools directly via stdio client (same as TodoAgent)
- **FR-003**: MockTodoAgent MUST return tool_calls array showing which tools were invoked
- **FR-004**: MockTodoAgent MUST provide user-friendly response messages confirming actions
- **FR-005**: MockTodoAgent MUST have identical method signature as TodoAgent: `run(user_id, messages, model) -> (response, tool_calls)`
- **FR-006**: MockTodoAgent MUST extract task titles from "add" commands (e.g., "Add buy groceries" -> title="buy groceries")
- **FR-007**: MockTodoAgent MUST extract task IDs from "complete/delete/update" commands
- **FR-008**: MockTodoAgent MUST detect status filters from "list" commands (all, pending, completed)
- **FR-009**: MockTodoAgent MUST handle unrecognized commands with helpful guidance message
- **FR-010**: MockTodoAgent MUST gracefully handle MCP connection failures

### Command Detection Patterns

The following keyword patterns trigger specific MCP tools:

| Keywords | Tool | Extraction |
|----------|------|------------|
| add, create, remember, need to | add_task | Text after keyword = title |
| show, list, what, tasks | list_tasks | "pending"/"completed"/"done" = status filter |
| complete, done, finish, mark | complete_task | UUID pattern = task_id |
| delete, remove, cancel | delete_task | UUID pattern = task_id |
| update, change, rename, modify | update_task | UUID + remaining text = task_id + new title |

### Key Entities

- **MockTodoAgent**: Drop-in replacement for TodoAgent when OpenAI is unavailable. Uses pattern matching instead of AI for intent detection.
- **ToolCallInfo**: Existing schema for recording tool invocations (tool_name, arguments, result).
- **MCP Client Session**: Stdio-based connection to MCP server for executing tools.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add tasks via natural language within 2 seconds (no AI latency)
- **SC-002**: Users can list tasks via natural language within 2 seconds
- **SC-003**: All 5 MCP tools (add, list, complete, delete, update) are accessible via MockTodoAgent
- **SC-004**: tool_calls array is populated for every successful operation (not empty)
- **SC-005**: Response messages are user-friendly and confirm the action taken
- **SC-006**: MockTodoAgent works as drop-in replacement (same interface as TodoAgent)
- **SC-007**: System remains functional when OpenAI API is unavailable

## Assumptions

- MCP server is running and accessible via stdio
- User is authenticated (user_id is available)
- Task IDs are UUIDs that can be pattern-matched from user input
- Single command per message (no multi-command parsing)
- English language only (no i18n in this enhancement)

## Out of Scope

- AI-powered intent detection (that's what TodoAgent does)
- Resolving task names to IDs (requires AI reasoning)
- Multi-turn conversation context (stateless per request)
- Voice input processing
- Multi-language support

## Dependencies

- Existing MCP server with 5 tools (add_task, list_tasks, complete_task, delete_task, update_task)
- Existing ToolCallInfo schema
- Existing conversation/message persistence (from 003-chat-mcp-server)