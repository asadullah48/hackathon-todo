# Hackathon Todo CLI

A command-line todo application with 5 essential operations.

## Features

- Add new tasks with title and optional description
- View all tasks with status indicators
- Update task title and description
- Delete tasks
- Toggle task completion status

## Installation

```bash
uv sync --dev
```

## Usage

```bash
uv run todo
```

## Development

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/
```
