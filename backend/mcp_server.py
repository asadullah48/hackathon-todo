"""MCP Server for Todo Task Management.

This server exposes task CRUD operations as MCP tools for AI agent integration.
It runs as a standalone subprocess and communicates via stdio.

Usage:
    python mcp_server.py
"""

import asyncio
import os
import sys
from uuid import UUID

import mcp.server.stdio
import mcp.types as types
from dotenv import load_dotenv
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from sqlalchemy import create_engine
from sqlmodel import Session, select

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.task import Task  # noqa: E402

# Get database URL and convert to sync version
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo")
# Remove asyncpg driver for sync connection and fix SSL parameter
SYNC_DATABASE_URL = (
    DATABASE_URL
    .replace("+asyncpg", "")
    .replace("postgresql://", "postgresql+psycopg2://")
    .replace("ssl=require", "sslmode=require")  # psycopg2 uses sslmode
)

# Create sync engine for MCP server
engine = create_engine(SYNC_DATABASE_URL, echo=False)

# Initialize MCP server
server = Server("todo-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools for task management."""
    return [
        types.Tool(
            name="add_task",
            description="Create a new todo task for the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User UUID (required for authorization)",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (1-200 characters)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional, max 1000 characters)",
                    },
                },
                "required": ["user_id", "title"],
            },
        ),
        types.Tool(
            name="list_tasks",
            description="List all tasks for the user, optionally filtered by status",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User UUID (required for authorization)",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by status: 'all', 'pending', or 'completed'",
                    },
                },
                "required": ["user_id"],
            },
        ),
        types.Tool(
            name="complete_task",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User UUID (required for authorization)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task UUID to mark as complete",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
        types.Tool(
            name="delete_task",
            description="Delete a task from the user's list",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User UUID (required for authorization)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task UUID to delete",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
        types.Tool(
            name="update_task",
            description="Update a task's title or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User UUID (required for authorization)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task UUID to update",
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional)",
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional)",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle MCP tool calls and route to appropriate handler."""
    if not arguments:
        raise ValueError("Missing arguments")

    user_id_str = arguments.get("user_id")
    if not user_id_str:
        raise ValueError("user_id is required for all task operations")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise ValueError(f"Invalid user_id format: {user_id_str}")

    # Route to appropriate handler
    handlers = {
        "add_task": add_task_handler,
        "list_tasks": list_tasks_handler,
        "complete_task": complete_task_handler,
        "delete_task": delete_task_handler,
        "update_task": update_task_handler,
    }

    handler = handlers.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")

    return await handler(user_id, arguments)


# ============ Tool Handlers ============


async def add_task_handler(
    user_id: UUID, args: dict
) -> list[types.TextContent]:
    """Add a new task for the user."""
    title = args.get("title", "").strip()
    if not title:
        return [types.TextContent(type="text", text="Error: Task title is required.")]

    description = args.get("description", "")

    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title[:200],  # Enforce max length
            description=description[:1000] if description else None,
            is_completed=False,
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return [
            types.TextContent(
                type="text",
                text=f"Task created successfully!\n- ID: {task.id}\n- Title: {task.title}",
            )
        ]


async def list_tasks_handler(
    user_id: UUID, args: dict
) -> list[types.TextContent]:
    """List tasks for the user with optional status filter."""
    status = args.get("status", "all").lower()

    with Session(engine) as session:
        query = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            query = query.where(Task.is_completed == False)  # noqa: E712
        elif status == "completed":
            query = query.where(Task.is_completed == True)  # noqa: E712

        query = query.order_by(Task.created_at.desc())
        tasks = session.exec(query).all()

        if not tasks:
            status_text = f" ({status})" if status != "all" else ""
            return [
                types.TextContent(
                    type="text",
                    text=f"No tasks found{status_text}. You can add tasks by telling me what you need to do!",
                )
            ]

        # Format task list
        lines = [f"Found {len(tasks)} task(s):\n"]
        for task in tasks:
            status_icon = "✓" if task.is_completed else "○"
            lines.append(f"{status_icon} [{task.id}] {task.title}")
            if task.description:
                lines.append(f"   └─ {task.description[:50]}...")

        return [types.TextContent(type="text", text="\n".join(lines))]


async def complete_task_handler(
    user_id: UUID, args: dict
) -> list[types.TextContent]:
    """Mark a task as completed."""
    task_id_str = args.get("task_id")
    if not task_id_str:
        return [types.TextContent(type="text", text="Error: task_id is required.")]

    try:
        task_id = UUID(task_id_str)
    except ValueError:
        return [
            types.TextContent(
                type="text",
                text=f"Error: Invalid task_id format: {task_id_str}",
            )
        ]

    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return [
                types.TextContent(
                    type="text",
                    text=f"Task not found with ID: {task_id}. Use list_tasks to see available tasks.",
                )
            ]

        if task.is_completed:
            return [
                types.TextContent(
                    type="text",
                    text=f"Task '{task.title}' is already completed!",
                )
            ]

        task.is_completed = True
        session.add(task)
        session.commit()

        return [
            types.TextContent(
                type="text",
                text=f"Task completed! ✓ '{task.title}'",
            )
        ]


async def delete_task_handler(
    user_id: UUID, args: dict
) -> list[types.TextContent]:
    """Delete a task."""
    task_id_str = args.get("task_id")
    if not task_id_str:
        return [types.TextContent(type="text", text="Error: task_id is required.")]

    try:
        task_id = UUID(task_id_str)
    except ValueError:
        return [
            types.TextContent(
                type="text",
                text=f"Error: Invalid task_id format: {task_id_str}",
            )
        ]

    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return [
                types.TextContent(
                    type="text",
                    text=f"Task not found with ID: {task_id}. Use list_tasks to see available tasks.",
                )
            ]

        title = task.title
        session.delete(task)
        session.commit()

        return [
            types.TextContent(
                type="text",
                text=f"Task deleted: '{title}'",
            )
        ]


async def update_task_handler(
    user_id: UUID, args: dict
) -> list[types.TextContent]:
    """Update a task's title or description."""
    task_id_str = args.get("task_id")
    if not task_id_str:
        return [types.TextContent(type="text", text="Error: task_id is required.")]

    try:
        task_id = UUID(task_id_str)
    except ValueError:
        return [
            types.TextContent(
                type="text",
                text=f"Error: Invalid task_id format: {task_id_str}",
            )
        ]

    new_title = args.get("title")
    new_description = args.get("description")

    if not new_title and new_description is None:
        return [
            types.TextContent(
                type="text",
                text="Error: Provide at least 'title' or 'description' to update.",
            )
        ]

    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return [
                types.TextContent(
                    type="text",
                    text=f"Task not found with ID: {task_id}. Use list_tasks to see available tasks.",
                )
            ]

        updates = []
        if new_title:
            task.title = new_title[:200]
            updates.append(f"title → '{new_title}'")
        if new_description is not None:
            task.description = new_description[:1000] if new_description else None
            updates.append(f"description → '{new_description[:50]}...'")

        session.add(task)
        session.commit()

        return [
            types.TextContent(
                type="text",
                text=f"Task updated: {', '.join(updates)}",
            )
        ]


async def main() -> None:
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="todo-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
