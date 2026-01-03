---
id: 0007
title: Specify MockAgent Enhancement
stage: spec
date: 2026-01-03
surface: agent
model: claude-opus-4-5-20251101
feature: 003-chat-mcp-server
branch: 002-web-todo-app
user: asadullahshafique
command: /sp.specify
labels: ["mock-agent", "mcp", "graceful-degradation", "pattern-matching"]
links:
  spec: specs/003-chat-mcp-server/mock-agent-spec.md
  ticket: null
  adr: null
  pr: https://github.com/asadullah48/hackathon-todo/pull/1
files:
  - specs/003-chat-mcp-server/mock-agent-spec.md
  - specs/003-chat-mcp-server/checklists/mock-agent-requirements.md
tests:
  - Checklist validation: PASS (16/16 items)
---

## Prompt

MockTodoAgent Enhancement - Pattern-based natural language command parsing that calls MCP tools directly without OpenAI. Features: detect keywords (add/show/list/complete/delete/update), extract task titles and IDs from messages, call MCP server via stdio client, return actual tool_calls array showing operations performed, provide helpful response messages. Must work as drop-in replacement when OpenAI API is unavailable. Supports same conversation interface as TodoAgent.

## Response snapshot

Created MockTodoAgent enhancement specification with:

**5 User Stories** (prioritized):
1. P1: Add tasks via natural language ("Add buy groceries")
2. P1: List tasks via natural language ("Show my tasks")
3. P2: Complete tasks via natural language ("Complete task [ID]")
4. P2: Delete tasks via natural language ("Delete task [ID]")
5. P3: Update tasks via natural language ("Update task [ID] to...")

**10 Functional Requirements**:
- FR-001 to FR-010 covering command detection, MCP tool calls, response formatting

**Command Detection Patterns**:
| Keywords | Tool | Extraction |
|----------|------|------------|
| add, create, remember | add_task | Text after keyword = title |
| show, list, what | list_tasks | Status filter detection |
| complete, done, finish | complete_task | UUID extraction |
| delete, remove | delete_task | UUID extraction |
| update, change | update_task | UUID + new title |

**7 Success Criteria**: All measurable and technology-agnostic

## Outcome

- Impact: Spec defines functional MockTodoAgent as drop-in replacement
- Tests: Quality checklist passed 16/16 items
- Files: 2 files created (spec + checklist)
- Next prompts: /sp.plan for implementation planning
- Reflection: Clear scope with well-defined command patterns

## Evaluation notes (flywheel)

- Failure modes observed: None - spec is complete
- Graders run and results (PASS/FAIL): Requirements checklist: PASS
- Prompt variant (if applicable): Standard sp.specify
- Next experiment (smallest change to try): Proceed to /sp.plan
