"""Main entry point for the todo CLI application."""

from src.cli.display import show_error, show_menu
from src.cli.handlers import (
    handle_add_task,
    handle_delete_task,
    handle_toggle_task,
    handle_update_task,
    handle_view_tasks,
)
from src.services.task_service import TaskService


def get_user_choice() -> str:
    """Get menu selection from user.

    Returns:
        The user's input stripped of whitespace.
    """
    return input("Select option (1-6): ").strip()


def main() -> None:
    """Run the main menu loop."""
    service = TaskService()

    print("\nWelcome to Todo List Manager!")

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == "1":
            handle_add_task(service)
        elif choice == "2":
            handle_view_tasks(service)
        elif choice == "3":
            handle_update_task(service)
        elif choice == "4":
            handle_delete_task(service)
        elif choice == "5":
            handle_toggle_task(service)
        elif choice == "6":
            print("\nGoodbye!\n")
            break
        else:
            show_error("Invalid option. Please select 1-6.")


if __name__ == "__main__":
    main()
