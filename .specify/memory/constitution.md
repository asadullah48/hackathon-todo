<!--
Sync Impact Report
==================
Version change: 2.0.0 → 3.0.0 (MAJOR - Phase III AI/MCP expansion)
Modified principles:
  - III. Simplicity First → Updated to include Phase III AI dependencies
Added sections:
  - IX. AI Integration Standards (Phase III)
  - Phase III Technology Stack (MCP, OpenAI Agents, Chat Infrastructure)
Removed sections: None
Templates requiring updates:
  - plan-template.md: ✅ Compatible (supports AI agent patterns)
  - spec-template.md: ✅ Compatible (no constitution-specific changes needed)
  - tasks-template.md: ✅ Compatible (supports AI feature split)
Follow-up TODOs: None

Previous Sync (2.0.0):
- III. Simplicity First → Updated to clarify Phase I vs Phase II dependency scope
- VII. API-First Design (Phase II)
- VIII. Full-Stack Standards (Phase II)
- Phase II Technology Stack (Frontend, Backend, Database, Auth, Deployment)
-->

# Hackathon Todo Constitution

## Core Principles

### I. Spec-Driven Development

All code MUST be generated from specifications. Manual coding without a prior specification is prohibited.

**Rationale**: Specifications ensure intentional design, reduce ambiguity, and create documentation as a natural byproduct. This approach prevents ad-hoc implementations and maintains traceability from requirements to code.

**Rules**:
- Every feature MUST have a spec.md before implementation begins
- Code generation MUST reference the specification
- Changes to behavior MUST first update the specification

### II. Python Best Practices

All Python code MUST follow PEP 8 style guidelines, use type hints, include docstrings, and maintain clean code structure.

**Rationale**: Consistent style reduces cognitive load, type hints enable static analysis and IDE support, docstrings provide inline documentation.

**Rules**:
- PEP 8 compliance is MANDATORY (enforced via linting)
- All public functions and classes MUST have docstrings
- Line length MUST NOT exceed 88 characters (Black formatter default)
- Imports MUST be organized: standard library, third-party, local

### III. Simplicity First

Use appropriate dependencies for each phase. Phase I uses standard library only; Phase II uses approved full-stack dependencies.

**Rationale**: External dependencies add complexity, security risks, and maintenance burden. Starting simple ensures the core logic is sound before adding complexity. Phase II expands scope with vetted dependencies for full-stack development.

**Rules**:
- Phase I: Standard library only (no pip install except dev tools)
- Phase I Data storage: Python dict/list in-memory structures
- Phase II: Approved dependencies only (see Technology Stack section)
- Phase II Data storage: PostgreSQL via SQLModel ORM
- Phase III: AI dependencies approved for chatbot functionality (MCP, OpenAI)
- Phase III: Stateless conversation management via database persistence
- New dependencies require explicit justification and ADR
- YAGNI (You Aren't Gonna Need It) principle applies to all phases

### IV. Modular Architecture

Separate concerns into distinct modules: models (data structures), business logic (services), CLI interface, and testing.

**Rationale**: Separation of concerns enables independent testing, easier maintenance, and clear responsibility boundaries.

**Rules**:
- Models: Data structures and validation only, no business logic
- Services: Business logic only, no I/O or CLI concerns
- CLI: User interface only, delegates to services
- Tests: Organized by type (unit, integration, contract)

### V. Type Safety

Use Python 3.13+ type hints everywhere. Enable static type checking.

**Rationale**: Type hints catch errors at development time, improve IDE support, and serve as executable documentation.

**Rules**:
- All function parameters and return values MUST have type hints
- All class attributes MUST have type annotations
- Generic types (list[str], dict[str, int]) MUST be used over bare types
- Type checking with mypy or pyright SHOULD pass without errors

### VI. Test-Driven Mindset

Every feature MUST be testable. Write clear, maintainable code that can be verified.

**Rationale**: Testable code is modular code. If code is hard to test, it's a design smell.

**Rules**:
- Pure functions preferred over stateful operations
- Dependencies MUST be injectable (no hardcoded globals)
- Side effects MUST be isolated and controllable
- Tests SHOULD be written before or alongside implementation

### VII. API-First Design (Phase II)

Design APIs before implementation. All endpoints MUST have clear contracts and documentation.

**Rationale**: API-first design ensures frontend and backend teams can work in parallel, enables automated testing, and provides self-documenting interfaces.

**Rules**:
- RESTful endpoints with clear HTTP semantics (GET reads, POST creates, PUT/PATCH updates, DELETE removes)
- OpenAPI/Swagger documentation MUST be maintained for all endpoints
- Stateless backend design: no server-side session storage
- JWT-based authentication for all protected endpoints
- API versioning strategy MUST be defined (path-based: /api/v1/)
- Error responses MUST follow consistent structure with error codes

### VIII. Full-Stack Standards (Phase II)

Adhere to modern full-stack development patterns for web applications.

**Rationale**: Consistent patterns across frontend and backend reduce cognitive load, improve maintainability, and leverage framework optimizations.

**Rules**:
- Frontend: Next.js App Router patterns MUST be followed
- Server Components by default; Client Components only when interactivity required
- TypeScript strict mode enabled for all frontend code
- Tailwind CSS for styling (no custom CSS unless justified)
- Better Auth for authentication flows
- Environment variables for all configuration (no hardcoded secrets)
- Responsive design MUST work on mobile and desktop

### IX. AI Integration Standards (Phase III)

Implement AI-powered features using standardized protocols and approved AI providers.

**Rationale**: AI integration requires careful design to ensure reliability, graceful degradation, and maintainability. Using standardized protocols (MCP) enables interoperability and future flexibility.

**Rules**:
- Model Context Protocol (MCP) MUST be used for tool exposure to AI agents
- MCP server runs as subprocess with stdio communication
- OpenAI Agents SDK for AI reasoning and tool orchestration
- Stateless chat endpoint: conversation state MUST persist in database, not memory
- Graceful degradation: MockAgent MUST be available when AI provider unavailable
- All AI interactions MUST be logged for debugging and audit
- API keys MUST be stored in environment variables, never in code
- Token usage and costs SHOULD be monitored

## Technology Stack

### Phase I (CLI Application)

**Language**: Python 3.12+
**Package Manager**: UV
**Runtime**: CPython
**Frameworks**: None (standard library only)
**Data Storage**: In-memory (list/dict)
**Testing**: pytest (development dependency only)
**Linting**: ruff (PEP 8 enforcement)
**Type Checking**: mypy or pyright

### Phase II (Full-Stack Web Application)

**Frontend**:
- Next.js 16+ with App Router
- TypeScript 5.x (strict mode)
- Tailwind CSS for styling
- Better Auth for authentication

**Backend**:
- FastAPI for REST API
- SQLModel for ORM
- Pydantic for validation
- Python 3.12+

**Database**:
- Neon PostgreSQL (serverless)
- SQLModel migrations

**Authentication**:
- Better Auth
- JWT tokens for API access

**Deployment**:
- Frontend: Vercel
- Backend: Render or Railway
- Database: Neon (managed PostgreSQL)

### Phase III (AI-Powered Chatbot)

**AI Infrastructure**:
- MCP (Model Context Protocol) >= 1.25.0 for tool standardization
- OpenAI SDK >= 2.14.0 for AI agent orchestration
- stdio subprocess communication for MCP server

**Chat Backend**:
- Conversation and Message models (SQLModel)
- ConversationService for state management
- Stateless chat API endpoint
- MockTodoAgent fallback for graceful degradation

**Chat Frontend**:
- Custom ChatContainer component
- Real-time message display
- Quick action buttons for common tasks
- Loading states and error handling

**Architecture Pattern**:
- MCP server exposes 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
- TodoAgent connects OpenAI to MCP tools via stdio
- Chat endpoint: load conversation → run agent → persist response
- JWT authentication for all chat endpoints

## Development Workflow

### Code Review Requirements
- All changes MUST be reviewed before merge
- Review checklist includes constitution compliance check
- Spec-to-code traceability MUST be verifiable

### Quality Gates
- Linting MUST pass (ruff)
- Type checking SHOULD pass (mypy/pyright)
- Tests MUST pass before merge
- Spec.md MUST be updated if behavior changes

### Deployment
- Phase I: Local development only
- No external service dependencies
- Configuration via environment variables (when needed)

## Governance

This constitution supersedes all other practices. It defines the non-negotiable rules for the Hackathon Todo project.

### Amendment Procedure
1. Propose amendment with rationale
2. Document as ADR if architecturally significant
3. Update constitution with version bump
4. Propagate changes to dependent templates

### Versioning Policy
- **MAJOR**: Backward-incompatible governance changes or principle removal
- **MINOR**: New principles added or material expansion
- **PATCH**: Clarifications, wording fixes, non-semantic changes

### Compliance Review
- All PRs MUST verify constitution compliance
- Complexity MUST be justified against Simplicity First principle
- Runtime guidance in CLAUDE.md for agent-specific instructions

**Version**: 3.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2026-01-03
