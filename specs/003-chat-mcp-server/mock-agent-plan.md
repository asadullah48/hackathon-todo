# Implementation Plan: MockTodoAgent Enhancement

**Branch**: `003-chat-mcp-server` (enhancement) | **Date**: 2026-01-03 | **Spec**: [mock-agent-spec.md](./mock-agent-spec.md)
**Input**: Feature specification from `/specs/003-chat-mcp-server/mock-agent-spec.md`

## Summary

Enhance MockTodoAgent to be a functional drop-in replacement for TodoAgent when OpenAI is unavailable. Instead of returning generic messages, MockTodoAgent will use pattern-based natural language parsing to detect command intent and call MCP tools directly via stdio client. This provides graceful degradation with actual task management functionality.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: MCP SDK (existing), regex (standard library)
**Storage**: N/A (uses existing MCP server which connects to PostgreSQL)
**Testing**: pytest with async support
**Target Platform**: Linux/macOS server (same as backend)
**Project Type**: Backend enhancement (single file modification)
**Performance Goals**: <2s response time (no AI latency)
**Constraints**: Must maintain identical interface to TodoAgent
**Scale/Scope**: Single class enhancement, ~150-200 lines of code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | mock-agent-spec.md created before implementation |
| II. Python Best Practices | PASS | Will follow PEP 8, type hints, docstrings |
| III. Simplicity First | PASS | Uses standard library regex, no new dependencies |
| IV. Modular Architecture | PASS | MockTodoAgent is self-contained in agents module |
| V. Type Safety | PASS | Will use full type hints, same signature as TodoAgent |
| VI. Test-Driven Mindset | PASS | Will add unit tests for pattern matching |
| IX. AI Integration Standards | PASS | Uses MCP protocol, provides graceful degradation |

**Gate Status**: ALL PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/003-chat-mcp-server/
├── spec.md                  # Main Phase 3 spec
├── mock-agent-spec.md       # MockAgent enhancement spec
├── mock-agent-plan.md       # This file
├── mock-agent-research.md   # Phase 0 output
├── mock-agent-data-model.md # Phase 1 output
├── contracts/
│   └── mock-agent.yaml      # Interface contract
├── quickstart.md            # Phase 3 quickstart (existing)
└── tasks.md                 # Phase 3 tasks (existing)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── todo_agent.py    # Contains MockTodoAgent (MODIFY)
│   └── ...
├── mcp_server.py            # MCP server (EXISTING)
└── tests/
    └── test_mock_agent.py   # New unit tests
```

**Structure Decision**: Enhancement to existing backend/src/agents/todo_agent.py file. No new files needed except optional test file.

## Complexity Tracking

No violations - enhancement uses existing infrastructure with standard library only.

## Design Decisions

### D1: Pattern Matching Strategy

**Decision**: Use regex patterns with keyword detection and extraction groups

**Rationale**:
- Standard library (re module) - no new dependencies
- Predictable behavior (deterministic, not probabilistic)
- Fast execution (<1ms for pattern matching)
- Easy to test and debug

**Patterns**:
```
ADD:      r'(?:add|create|remember|need to)\s+(.+)'
LIST:     r'(?:show|list|what|display).*(?:tasks?|todo)'
COMPLETE: r'(?:complete|done|finish|mark).*([0-9a-f-]{36})'
DELETE:   r'(?:delete|remove|cancel).*([0-9a-f-]{36})'
UPDATE:   r'(?:update|change|rename|modify).*([0-9a-f-]{36}).*(?:to|title)\s+["\']?(.+?)["\']?\s*$'
```

### D2: MCP Client Integration

**Decision**: Reuse TodoAgent's MCP client connection pattern

**Rationale**:
- Consistent with existing architecture
- MCP stdio client already proven to work
- Same tool call flow as TodoAgent

### D3: Response Formatting

**Decision**: Format responses to match MCP tool output style

**Rationale**:
- Consistent user experience whether using AI or pattern matching
- Tool results already formatted nicely by MCP server
- Add "Demo Mode" indicator for transparency

## Implementation Approach

### Phase 1: Command Parser Module

1. Create `CommandParser` class with pattern matching methods
2. Implement `detect_intent()` -> returns (command_type, extracted_args)
3. Handle edge cases (no match, multiple matches, empty input)

### Phase 2: MCP Integration

1. Add async `_connect_mcp()` method to MockTodoAgent
2. Implement `_call_tool()` method reusing TodoAgent's pattern
3. Handle MCP connection errors gracefully

### Phase 3: Run Method

1. Parse user message with CommandParser
2. If command detected: call appropriate MCP tool
3. Build ToolCallInfo array from results
4. Return formatted response with tool_calls

### Phase 4: Testing

1. Unit tests for pattern matching (parameterized)
2. Integration test with MCP server
3. Edge case tests (empty, no match, MCP failure)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Pattern doesn't match valid commands | Comprehensive test suite, fallback help message |
| MCP server unavailable | Graceful error with retry guidance |
| UUID extraction fails | Strict UUID pattern, clear error message |
| Performance regression | Pattern matching is O(1), no concern |
