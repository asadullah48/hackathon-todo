# Gemini Project: hackathon-todo

## Project Overview

This project is a command-line todo application written in Python. It allows users to manage a list of tasks with the following operations:

*   **Add Task:** Create a new task with a title and an optional description.
*   **View Tasks:** Display all tasks with their ID, status, title, and description.
*   **Update Task:** Modify the title and/or description of an existing task.
*   **Delete Task:** Remove a task from the list.
*   **Toggle Status:** Mark a task as complete or incomplete.

The application is built with a simple, layered architecture:

*   **CLI (`src/cli`):** Handles user interaction, input parsing, and displaying output.
*   **Services (`src/services`):** Implements the core business logic for task management.
*   **Models (`src/models`):** Defines the data structure for a task.

The project uses `pytest` for testing, `ruff` for linting, and `mypy` for static type checking.

## Building and Running

### Setup

1.  **Install Python:** Make sure you have Python 3.13 or higher installed.
2.  **Install Dependencies:**
    ```bash
    pip install -e .[dev]
    ```

### Running the Application

To run the todo application, use the following command:

```bash
todo
```

### Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

## Development Conventions

*   **Linting:** The project uses `ruff` for code formatting and linting. Before committing, run `ruff check .` to ensure your code adheres to the style guide.
*   **Type Checking:** `mypy` is used for static type checking. Run `mypy src` to check for type errors.
*   **Testing:** All new features should be accompanied by unit tests. The tests are located in the `tests/` directory.
