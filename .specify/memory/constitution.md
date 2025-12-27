<!--
Sync Impact Report
==================
Version change: 0.0.0 → 1.0.0 (Initial ratification)
Modified principles: N/A (new constitution)
Added sections:
  - 6 Core Principles (Spec-Driven, Python Best Practices, Simplicity First, Modular Architecture, Type Safety, Test-Driven Mindset)
  - Technology Stack section
  - Development Workflow section
  - Governance section
Removed sections: N/A
Templates requiring updates:
  - plan-template.md: ✅ Compatible (references constitution check)
  - spec-template.md: ✅ Compatible (no constitution-specific changes needed)
  - tasks-template.md: ✅ Compatible (no constitution-specific changes needed)
Follow-up TODOs: None
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

Use Python standard library only for Phase I. No external dependencies. In-memory storage only.

**Rationale**: External dependencies add complexity, security risks, and maintenance burden. Starting simple ensures the core logic is sound before adding complexity.

**Rules**:
- Phase I: Standard library only (no pip install except dev tools)
- Data storage: Python dict/list in-memory structures
- External dependencies require explicit justification and ADR
- YAGNI (You Aren't Gonna Need It) principle applies

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

## Technology Stack

**Language**: Python 3.13+
**Package Manager**: UV
**Runtime**: CPython
**Frameworks**: None (standard library only for Phase I)
**Data Storage**: In-memory (list/dict)
**Testing**: pytest (development dependency only)
**Linting**: ruff (PEP 8 enforcement)
**Type Checking**: mypy or pyright

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

**Version**: 1.0.0 | **Ratified**: 2025-12-27 | **Last Amended**: 2025-12-27
