# Todo List Manager - QWEN Context

## Project Overview

This is a command-line todo application built in Python that provides 5 essential operations for task management. The application features a clean, menu-driven interface with in-memory storage for tasks.

**Key Features:**
- Add tasks with titles and optional descriptions
- View all tasks in a formatted table
- Update existing tasks
- Delete tasks permanently
- Toggle task completion status
- Input validation for all user inputs
- Clean, user-friendly CLI interface

**Architecture:**
- **CLI Layer**: Menu-driven interface with handlers for each operation
- **Service Layer**: Business logic in TaskService with in-memory storage
- **Model Layer**: Task data model with validation
- **Library Layer**: Input validation utilities
- **Testing**: Comprehensive unit tests using pytest

## Building and Running

### Prerequisites
- Python 3.13 or higher

### Setup
```bash
# Install the package in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Running the Application
```bash
# Run the CLI application
todo

# Or run directly with Python
python -m src.cli.main
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_task_service.py
```

### Code Quality
```bash
# Lint the code
ruff check src tests

# Format the code
ruff format src tests

# Type checking
mypy src
```

## Development Conventions

### Code Style
- Follow PEP 8 guidelines
- Use Ruff for linting and formatting
- Type hints required for all public functions
- Docstrings in Google format for all public functions and classes

### Architecture Patterns
- **Separation of Concerns**: CLI, business logic, and data models are separated
- **In-Memory Storage**: Tasks are stored in a list within TaskService
- **Validation**: Input validation occurs at both CLI and service layers
- **Error Handling**: Custom exceptions for specific error cases

### File Structure
```
src/
├── cli/                 # Command-line interface components
│   ├── main.py          # Main application entry point
│   ├── handlers.py      # Menu option handlers
│   └── display.py       # UI formatting and display functions
├── models/              # Data models
│   └── task.py          # Task data class
├── services/            # Business logic
│   └── task_service.py  # Task management service
└── lib/                 # Utility functions
    └── validators.py    # Input validation functions
tests/
├── unit/                # Unit tests for individual components
│   ├── test_task_model.py
│   ├── test_task_service.py
│   └── test_validators.py
└── integration/         # Integration tests (currently empty)
```

### Task Model
- `id`: Unique positive integer identifier (auto-generated)
- `title`: Required text (1-200 characters)
- `description`: Optional text (0-1000 characters)
- `completed`: Boolean status (defaults to False)
- `created_at`: Timestamp of creation

### CLI Operations
1. **Add Task**: Create new tasks with title and optional description
2. **View Tasks**: Display all tasks in a formatted table
3. **Update Task**: Modify existing task title or description
4. **Delete Task**: Remove tasks permanently
5. **Toggle Status**: Switch between complete/incomplete states
6. **Exit**: Quit the application

### Validation Rules
- Task title: 1-200 characters, cannot be empty or whitespace-only
- Task description: 0-1000 characters
- Task ID: Positive integer only
- All validation errors are caught and displayed to the user

### Testing Strategy
- Unit tests for all service methods
- Test edge cases and error conditions
- 100% coverage of business logic
- Parameterized tests where appropriate
- Mock-free testing using pure unit tests

## Key Classes and Functions

### TaskService
- `add_task(title, description)`: Create new task
- `get_task(task_id)`: Retrieve single task
- `get_all_tasks()`: Retrieve all tasks
- `update_task(task_id, title, description)`: Update task fields
- `delete_task(task_id)`: Remove task
- `toggle_task(task_id)`: Toggle completion status

### Validators
- `validate_title(title)`: Check title validity
- `validate_description(description)`: Check description validity
- `validate_task_id(task_id_str)`: Parse and validate task ID

## Error Handling
- `TaskNotFoundError`: Raised when operations target non-existent tasks
- `ValidationError`: Raised when input validation fails
- User-friendly error messages displayed in CLI