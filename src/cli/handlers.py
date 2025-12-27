"""CLI handlers for menu operations."""

from src.cli.display import (
    COMPLETE_INDICATOR,
    INCOMPLETE_INDICATOR,
    format_task_list,
    show_error,
    show_message,
)
from src.lib.validators import validate_description, validate_task_id, validate_title
from src.services.task_service import TaskNotFoundError, TaskService, ValidationError


def handle_add_task(service: TaskService) -> None:
    """Handle the add task menu option.

    Args:
        service: The TaskService instance.
    """
    print("\n=== ADD TASK ===")

    # Get and validate title
    title = input("Title: ").strip()
    is_valid, error = validate_title(title)
    if not is_valid:
        show_error(error)
        return

    # Get and validate description (optional)
    description = input("Description (optional): ").strip()
    is_valid, error = validate_description(description)
    if not is_valid:
        show_error(error)
        return

    # Create the task
    try:
        task = service.add_task(title, description)
        show_message(f"Task created with ID: {task.id}")
    except ValidationError as e:
        show_error(str(e))


def handle_view_tasks(service: TaskService) -> None:
    """Handle the view tasks menu option.

    Args:
        service: The TaskService instance.
    """
    tasks = service.get_all_tasks()
    print(format_task_list(tasks))


def handle_update_task(service: TaskService) -> None:
    """Handle the update task menu option.

    Args:
        service: The TaskService instance.
    """
    print("\n=== UPDATE TASK ===")

    # Get and validate task ID
    task_id_str = input("Task ID: ").strip()
    is_valid, task_id, error = validate_task_id(task_id_str)
    if not is_valid:
        show_error(error)
        return

    # Check task exists and show current values
    task = service.get_task(task_id)  # type: ignore[arg-type]
    if task is None:
        show_error(f"Task not found: {task_id}")
        return

    print(f"\nCurrent title: {task.title}")
    print(f"Current description: {task.description or '(none)'}")

    # Get new values
    new_title = input("\nNew title (press Enter to keep current): ").strip()
    new_description = input("New description (press Enter to keep current): ").strip()

    # Validate new title if provided
    if new_title:
        is_valid, error = validate_title(new_title)
        if not is_valid:
            show_error(error)
            return

    # Validate new description if provided
    if new_description:
        is_valid, error = validate_description(new_description)
        if not is_valid:
            show_error(error)
            return

    # Update the task
    try:
        updated_task = service.update_task(
            task_id,  # type: ignore[arg-type]
            title=new_title if new_title else None,
            description=new_description if new_description else None,
        )
        show_message(f"Task {updated_task.id} updated successfully")
    except (TaskNotFoundError, ValidationError) as e:
        show_error(str(e))


def handle_delete_task(service: TaskService) -> None:
    """Handle the delete task menu option.

    Args:
        service: The TaskService instance.
    """
    print("\n=== DELETE TASK ===")

    # Get and validate task ID
    task_id_str = input("Task ID: ").strip()
    is_valid, task_id, error = validate_task_id(task_id_str)
    if not is_valid:
        show_error(error)
        return

    # Delete the task
    try:
        service.delete_task(task_id)  # type: ignore[arg-type]
        show_message(f"Task {task_id} deleted successfully")
    except TaskNotFoundError as e:
        show_error(str(e))


def handle_toggle_task(service: TaskService) -> None:
    """Handle the toggle task status menu option.

    Args:
        service: The TaskService instance.
    """
    print("\n=== TOGGLE STATUS ===")

    # Get and validate task ID
    task_id_str = input("Task ID: ").strip()
    is_valid, task_id, error = validate_task_id(task_id_str)
    if not is_valid:
        show_error(error)
        return

    # Toggle the task
    try:
        task = service.toggle_task(task_id)  # type: ignore[arg-type]
        status = "complete" if task.completed else "incomplete"
        indicator = COMPLETE_INDICATOR if task.completed else INCOMPLETE_INDICATOR
        show_message(f"Task {task.id} marked as {status} {indicator}")
    except TaskNotFoundError as e:
        show_error(str(e))
