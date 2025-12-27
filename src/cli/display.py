"""Display utilities for the todo CLI."""

from src.models.task import Task

# Status indicators
INCOMPLETE_INDICATOR = "○"
COMPLETE_INDICATOR = "✓"


def format_task(task: Task) -> str:
    """Format a single task for display.

    Args:
        task: The task to format.

    Returns:
        Formatted string representation of the task.
    """
    status = COMPLETE_INDICATOR if task.completed else INCOMPLETE_INDICATOR
    desc = f" - {task.description}" if task.description else ""
    return f"[{task.id}] {status} {task.title}{desc}"


def format_task_list(tasks: list[Task]) -> str:
    """Format a list of tasks for display.

    Args:
        tasks: List of tasks to format.

    Returns:
        Formatted string with all tasks, or empty list message.
    """
    if not tasks:
        return "No tasks yet. Add your first task!"

    lines = ["", "=== YOUR TASKS ===", ""]

    # Table header
    lines.append(f"{'ID':<4} {'Status':<6} {'Title':<30} {'Description':<40}")
    lines.append("-" * 82)

    for task in tasks:
        status = COMPLETE_INDICATOR if task.completed else INCOMPLETE_INDICATOR
        title = task.title[:30] if len(task.title) <= 30 else task.title[:27] + "..."
        desc = task.description[:40] if len(task.description) <= 40 else task.description[:37] + "..."
        lines.append(f"{task.id:<4} {status:<6} {title:<30} {desc:<40}")

    lines.append("")
    return "\n".join(lines)


def show_message(message: str) -> None:
    """Display a success message.

    Args:
        message: The message to display.
    """
    print(f"\n✓ {message}\n")


def show_error(message: str) -> None:
    """Display an error message.

    Args:
        message: The error message to display.
    """
    print(f"\n✗ Error: {message}\n")


def show_menu() -> None:
    """Display the main menu."""
    menu = """
╔═══════════════════════════════════════╗
║         TODO LIST MANAGER             ║
╠═══════════════════════════════════════╣
║  1. Add Task                          ║
║  2. View Tasks                        ║
║  3. Update Task                       ║
║  4. Delete Task                       ║
║  5. Toggle Complete/Incomplete        ║
║  6. Exit                              ║
╚═══════════════════════════════════════╝
"""
    print(menu)
