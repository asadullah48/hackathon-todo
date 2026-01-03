# Data Model: MockTodoAgent Enhancement

**Date**: 2026-01-03
**Feature**: MockTodoAgent Pattern-Based Command Parsing
**Related Spec**: [mock-agent-spec.md](./mock-agent-spec.md)

## Overview

MockTodoAgent enhancement does not introduce new database entities. It operates on existing entities via MCP tools. This document describes the internal data structures used for command parsing and tool invocation.

## Internal Data Structures

### CommandType Enum

Represents the type of command detected from user input.

```
CommandType:
  - ADD: Create a new task
  - LIST: Retrieve tasks
  - COMPLETE: Mark task as done
  - DELETE: Remove a task
  - UPDATE: Modify task properties
  - UNKNOWN: No command detected
```

### ParsedCommand

Result of parsing a user message.

| Field | Type | Description |
|-------|------|-------------|
| command_type | CommandType | Detected command type |
| task_title | str | None | Extracted task title (for ADD) |
| task_id | str | None | Extracted task UUID (for COMPLETE/DELETE/UPDATE) |
| status_filter | str | Status filter: "all", "pending", "completed" (for LIST) |
| new_title | str | None | New title (for UPDATE) |
| raw_message | str | Original user message |
| confidence | float | Match confidence (1.0 for exact, 0.0 for no match) |

### ToolCallInfo (Existing)

Already defined in `src/schemas/chat.py`. Used to record tool invocations.

| Field | Type | Description |
|-------|------|-------------|
| tool_name | str | Name of MCP tool called |
| arguments | dict | Arguments passed to tool |
| result | str | Tool execution result |

## Entity Relationships

```
User Input (message)
      │
      ▼
┌─────────────────┐
│ CommandParser   │
│ (pattern match) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ParsedCommand   │
│ (internal DTO)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ MockTodoAgent   │────▶│ MCP Server      │
│ (orchestrator)  │     │ (tool executor) │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │ Database        │
         │              │ (Task table)    │
         │              └─────────────────┘
         │
         ▼
┌─────────────────┐
│ ToolCallInfo[]  │
│ (response data) │
└─────────────────┘
```

## Existing Entities Used (No Changes)

### Task (from Phase 2)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner reference |
| title | str | Task title (1-200 chars) |
| description | str | None | Optional description |
| is_completed | bool | Completion status |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Conversation (from Phase 3)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner reference |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Message (from Phase 3)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | Parent conversation |
| role | str | "user" or "assistant" |
| content | str | Message text |
| created_at | datetime | Creation timestamp |

## State Transitions

MockTodoAgent is stateless - no internal state maintained between calls.

```
Request Flow:
1. IDLE → PARSING (receive message)
2. PARSING → CONNECTING (command detected)
3. CONNECTING → EXECUTING (MCP session ready)
4. EXECUTING → RESPONDING (tool result received)
5. RESPONDING → IDLE (response returned)

Error States:
- PARSING → IDLE (no command detected, return help)
- CONNECTING → IDLE (MCP error, return error message)
- EXECUTING → IDLE (tool error, return error message)
```

## Validation Rules

### ParsedCommand Validation

| Field | Rule |
|-------|------|
| task_title | Required for ADD, 1-200 characters |
| task_id | Required for COMPLETE/DELETE/UPDATE, valid UUID format |
| status_filter | Must be "all", "pending", or "completed" |
| new_title | Required for UPDATE, 1-200 characters |

### Message Input Validation

| Rule | Handling |
|------|----------|
| Empty message | Return prompt for command |
| Message > 10,000 chars | Truncate to 10,000 |
| No command detected | Return help message |
