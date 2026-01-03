"""TodoAgent - AI agent for task management using OpenAI and MCP.

This agent connects to the MCP server to execute task operations
based on natural language user requests.

MockTodoAgent provides graceful degradation with pattern-based
command parsing when OpenAI API is unavailable.
"""

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

from src.config import get_settings
from src.schemas.chat import ToolCallInfo

# T003: CommandType type alias
CommandType = Literal["add", "list", "complete", "delete", "update", "unknown"]

# T002: COMMAND_PATTERNS dict with regex patterns
COMMAND_PATTERNS: dict[str, re.Pattern[str]] = {
    "add": re.compile(
        r"(?:add|create|remember|need\s+to|have\s+to|i\s+need\s+to)\s+"
        r"(?:a\s+)?(?:task\s+(?:to\s+)?)?(.+)",
        re.IGNORECASE,
    ),
    "list": re.compile(
        r"(?:show|list|what|display|get|see|view).*?"
        r"(?:tasks?|todos?|pending|completed|done|left|remaining)",
        re.IGNORECASE,
    ),
    "complete": re.compile(
        r"(?:complete|done|finish|mark).*?"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        re.IGNORECASE,
    ),
    "delete": re.compile(
        r"(?:delete|remove|cancel).*?"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        re.IGNORECASE,
    ),
    "update": re.compile(
        r"(?:update|change|rename|modify).*?"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*?"
        r"(?:to|title|name)\s+[\"']?(.+?)[\"']?\s*$",
        re.IGNORECASE,
    ),
}

# UUID pattern for extraction
UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


# T004: ParsedCommand dataclass
@dataclass
class ParsedCommand:
    """Result of parsing a user message for command intent."""

    command_type: CommandType
    task_title: str | None = None
    task_id: str | None = None
    status_filter: str = "all"
    new_title: str | None = None


# System prompt for the todo agent
SYSTEM_PROMPT = """You are a helpful todo list assistant. Your job is to help users manage their tasks.

You have access to the following tools for task management:
- add_task: Create a new task
- list_tasks: View all tasks (can filter by status: all, pending, completed)
- complete_task: Mark a task as done
- delete_task: Remove a task
- update_task: Change a task's title or description

IMPORTANT RULES:
1. ALWAYS use the tools to perform task operations. Never pretend to perform actions.
2. When the user asks to see their tasks, use list_tasks first.
3. When completing or deleting a task, you need the task_id. If the user refers to a task by name, list_tasks first to find the ID.
4. Be concise but friendly in your responses.
5. After performing an action, confirm what was done.
6. If a tool returns an error, explain it to the user in simple terms.

Examples of user requests and how to handle them:
- "Add buy groceries" → use add_task with title="buy groceries"
- "Show my tasks" → use list_tasks with status="all"
- "Complete the groceries task" → first list_tasks to find ID, then complete_task
- "Delete task about meeting" → first list_tasks to find ID, then delete_task
- "What's left to do?" → use list_tasks with status="pending"
"""


class TodoAgent:
    """AI agent that manages tasks using OpenAI and MCP tools."""

    def __init__(self, openai_api_key: str | None = None) -> None:
        """Initialize the agent with OpenAI client.

        Args:
            openai_api_key: Optional API key. If not provided, uses environment.
        """
        settings = get_settings()
        api_key = openai_api_key or settings.openai_api_key

        if not api_key:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable or pass to constructor."
            )

        self.client = OpenAI(api_key=api_key)
        self.mcp_server_path = str(
            Path(__file__).parent.parent.parent / "mcp_server.py"
        )

    def _convert_mcp_tools_to_openai(self, mcp_tools: list[Any]) -> list[dict]:
        """Convert MCP tool definitions to OpenAI function format."""
        openai_tools = []
        for tool in mcp_tools:
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
            )
        return openai_tools

    async def _call_mcp_tool(
        self,
        session: ClientSession,
        tool_name: str,
        arguments: dict,
        user_id: str,
    ) -> str:
        """Call an MCP tool and return the result text.

        Automatically injects user_id into all tool calls for authorization.
        """
        # Always inject user_id for authorization
        arguments["user_id"] = user_id

        result = await session.call_tool(tool_name, arguments=arguments)

        # Extract text content from result
        if result.content:
            return result.content[0].text
        return "Tool executed successfully."

    async def run(
        self,
        user_id: str,
        messages: list[dict[str, str]],
        model: str = "gpt-4o-mini",
    ) -> tuple[str, list[ToolCallInfo]]:
        """Run the agent with the given messages.

        Args:
            user_id: UUID string of the authenticated user
            messages: Conversation history [{"role": "...", "content": "..."}]
            model: OpenAI model to use

        Returns:
            Tuple of (response_text, list_of_tool_calls)
        """
        tool_calls_made: list[ToolCallInfo] = []

        # Connect to MCP server via stdio
        server_params = StdioServerParameters(
            command="python",
            args=[self.mcp_server_path],
            env={**os.environ},  # Pass environment to MCP server
        )

        async with (
            stdio_client(server_params) as (read, write),
            ClientSession(read, write) as mcp_session,
        ):
            await mcp_session.initialize()

            # Get available tools from MCP server
            tools_result = await mcp_session.list_tools()
            mcp_tools = tools_result.tools
            openai_tools = self._convert_mcp_tools_to_openai(mcp_tools)

            # Build messages with system prompt
            full_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages,
            ]

            # Call OpenAI with tools
            response = self.client.chat.completions.create(
                model=model,
                messages=full_messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None,
            )

            assistant_message = response.choices[0].message

            # Handle tool calls
            while assistant_message.tool_calls:
                # Process each tool call
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    # Execute MCP tool
                    result_text = await self._call_mcp_tool(
                        mcp_session,
                        func_name,
                        func_args,
                        user_id,
                    )

                    # Record tool call
                    tool_calls_made.append(
                        ToolCallInfo(
                            tool_name=func_name,
                            arguments=func_args,
                            result=result_text,
                        )
                    )

                    tool_results.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text,
                        }
                    )

                # Add assistant message and tool results to conversation
                full_messages.append(
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in assistant_message.tool_calls
                        ],
                    }
                )
                full_messages.extend(tool_results)

                # Get next response from OpenAI
                response = self.client.chat.completions.create(
                    model=model,
                    messages=full_messages,
                    tools=openai_tools if openai_tools else None,
                    tool_choice="auto" if openai_tools else None,
                )
                assistant_message = response.choices[0].message

            # Return final text response
            return assistant_message.content or "", tool_calls_made


class MockTodoAgent:
    """Pattern-based agent for task management when OpenAI is unavailable.

    Uses regex patterns to detect command intent and calls MCP tools directly.
    Provides graceful degradation with actual task management functionality.
    """

    def __init__(self) -> None:
        """Initialize MockTodoAgent with MCP server path."""
        self.mcp_server_path = str(
            Path(__file__).parent.parent.parent / "mcp_server.py"
        )

    # T005: Parse command from message
    def _parse_command(self, message: str) -> ParsedCommand:
        """Detect command type and extract arguments from user message.

        Args:
            message: User's natural language message

        Returns:
            ParsedCommand with detected intent and extracted arguments
        """
        message = message.strip()

        # T032: Handle empty message
        if not message:
            return ParsedCommand(command_type="unknown")

        # Check each pattern in order of specificity
        # Update pattern (most specific - requires UUID + new title)
        match = COMMAND_PATTERNS["update"].search(message)
        if match:
            return ParsedCommand(
                command_type="update",
                task_id=match.group(1).lower(),
                new_title=self._extract_new_title(message, match.group(2)),
            )

        # Complete pattern
        match = COMMAND_PATTERNS["complete"].search(message)
        if match:
            return ParsedCommand(
                command_type="complete",
                task_id=match.group(1).lower(),
            )

        # Delete pattern
        match = COMMAND_PATTERNS["delete"].search(message)
        if match:
            return ParsedCommand(
                command_type="delete",
                task_id=match.group(1).lower(),
            )

        # Add pattern
        match = COMMAND_PATTERNS["add"].search(message)
        if match:
            return ParsedCommand(
                command_type="add",
                task_title=self._extract_task_title(match.group(1)),
            )

        # List pattern (least specific)
        match = COMMAND_PATTERNS["list"].search(message)
        if match:
            return ParsedCommand(
                command_type="list",
                status_filter=self._detect_status_filter(message),
            )

        # T033: No command recognized
        return ParsedCommand(command_type="unknown")

    # T006: Extract task title from add commands
    def _extract_task_title(self, raw_title: str) -> str:
        """Clean and extract task title from captured group.

        Args:
            raw_title: Raw captured text after trigger words

        Returns:
            Cleaned task title (max 200 chars)
        """
        # Remove common filler words and clean up
        title = raw_title.strip()
        # Remove leading articles and prepositions
        title = re.sub(r"^(?:a|an|the|to)\s+", "", title, flags=re.IGNORECASE)
        # Remove trailing punctuation
        title = title.rstrip(".,!?")
        return title[:200]

    # T007: Extract UUID from commands
    def _extract_uuid(self, message: str) -> str | None:
        """Extract UUID from message text.

        Args:
            message: User message that may contain a UUID

        Returns:
            Lowercase UUID string or None if not found
        """
        match = UUID_PATTERN.search(message)
        return match.group(0).lower() if match else None

    # T008: Detect status filter for list command
    def _detect_status_filter(self, message: str) -> str:
        """Detect status filter (all/pending/completed) from list command.

        Args:
            message: User message requesting task list

        Returns:
            One of: 'all', 'pending', 'completed'
        """
        message_lower = message.lower()

        # Check for pending indicators
        pending_words = [
            "pending",
            "left",
            "remaining",
            "todo",
            "incomplete",
            "not done",
        ]
        if any(word in message_lower for word in pending_words):
            return "pending"

        # Check for completed indicators
        completed_words = ["completed", "done", "finished"]
        if any(word in message_lower for word in completed_words):
            return "completed"

        return "all"

    # T028: Extract new title for update command
    def _extract_new_title(self, _message: str, captured: str) -> str:
        """Extract new title from update command.

        Args:
            _message: Full user message (reserved for future use)
            captured: Text captured by regex group

        Returns:
            Cleaned new title (max 200 chars)
        """
        title = captured.strip()
        # Remove quotes
        title = title.strip("\"'")
        return title[:200]

    # T009: Get help message for unrecognized commands
    def _get_help_message(self) -> str:
        """Return usage instructions for unrecognized commands.

        Returns:
            Help message with command examples
        """
        return (
            "[Demo Mode] I didn't recognize that command. Here's what I can do:\n\n"
            "- **Add a task**: 'Add buy groceries' or 'Remember to call mom'\n"
            "- **List tasks**: 'Show my tasks' or 'What's pending?'\n"
            "- **Complete task**: 'Complete task [paste-task-id-here]'\n"
            "- **Delete task**: 'Delete task [paste-task-id-here]'\n"
            "- **Update task**: 'Update task [id] to new title'\n\n"
            "Tip: Use 'Show my tasks' first to see task IDs, then copy-paste the ID."
        )

    # T011: Call add_task MCP tool
    async def _call_add_task(
        self, session: ClientSession, user_id: str, title: str
    ) -> tuple[str, ToolCallInfo]:
        """Invoke add_task MCP tool.

        Args:
            session: Active MCP session
            user_id: User UUID for authorization
            title: Task title to create

        Returns:
            Tuple of (result_text, tool_call_info)
        """
        arguments = {"user_id": user_id, "title": title}
        result = await session.call_tool("add_task", arguments=arguments)
        result_text = result.content[0].text if result.content else "Task created."

        tool_call = ToolCallInfo(
            tool_name="add_task",
            arguments=arguments,
            result=result_text,
        )
        return result_text, tool_call

    # T015: Call list_tasks MCP tool
    async def _call_list_tasks(
        self, session: ClientSession, user_id: str, status: str
    ) -> tuple[str, ToolCallInfo]:
        """Invoke list_tasks MCP tool.

        Args:
            session: Active MCP session
            user_id: User UUID for authorization
            status: Filter status ('all', 'pending', 'completed')

        Returns:
            Tuple of (result_text, tool_call_info)
        """
        arguments = {"user_id": user_id, "status": status}
        result = await session.call_tool("list_tasks", arguments=arguments)
        result_text = result.content[0].text if result.content else "No tasks found."

        tool_call = ToolCallInfo(
            tool_name="list_tasks",
            arguments=arguments,
            result=result_text,
        )
        return result_text, tool_call

    # T019: Call complete_task MCP tool
    async def _call_complete_task(
        self, session: ClientSession, user_id: str, task_id: str
    ) -> tuple[str, ToolCallInfo]:
        """Invoke complete_task MCP tool.

        Args:
            session: Active MCP session
            user_id: User UUID for authorization
            task_id: Task UUID to complete

        Returns:
            Tuple of (result_text, tool_call_info)
        """
        arguments = {"user_id": user_id, "task_id": task_id}
        result = await session.call_tool("complete_task", arguments=arguments)
        result_text = result.content[0].text if result.content else "Task completed."

        tool_call = ToolCallInfo(
            tool_name="complete_task",
            arguments=arguments,
            result=result_text,
        )
        return result_text, tool_call

    # T023: Call delete_task MCP tool
    async def _call_delete_task(
        self, session: ClientSession, user_id: str, task_id: str
    ) -> tuple[str, ToolCallInfo]:
        """Invoke delete_task MCP tool.

        Args:
            session: Active MCP session
            user_id: User UUID for authorization
            task_id: Task UUID to delete

        Returns:
            Tuple of (result_text, tool_call_info)
        """
        arguments = {"user_id": user_id, "task_id": task_id}
        result = await session.call_tool("delete_task", arguments=arguments)
        result_text = result.content[0].text if result.content else "Task deleted."

        tool_call = ToolCallInfo(
            tool_name="delete_task",
            arguments=arguments,
            result=result_text,
        )
        return result_text, tool_call

    # T027: Call update_task MCP tool
    async def _call_update_task(
        self, session: ClientSession, user_id: str, task_id: str, title: str
    ) -> tuple[str, ToolCallInfo]:
        """Invoke update_task MCP tool.

        Args:
            session: Active MCP session
            user_id: User UUID for authorization
            task_id: Task UUID to update
            title: New task title

        Returns:
            Tuple of (result_text, tool_call_info)
        """
        arguments = {"user_id": user_id, "task_id": task_id, "title": title}
        result = await session.call_tool("update_task", arguments=arguments)
        result_text = result.content[0].text if result.content else "Task updated."

        tool_call = ToolCallInfo(
            tool_name="update_task",
            arguments=arguments,
            result=result_text,
        )
        return result_text, tool_call

    async def run(
        self,
        user_id: str,
        messages: list[dict[str, str]],
        model: str = "gpt-4o-mini",  # noqa: ARG002
    ) -> tuple[str, list[ToolCallInfo]]:
        """Execute pattern-based command parsing and MCP tool invocation.

        Parses the last user message for command intent, connects to MCP server,
        and executes the appropriate tool. Returns response with tool_calls.

        Args:
            user_id: UUID string of the authenticated user
            messages: Conversation history [{"role": "...", "content": "..."}]
            model: Model parameter (ignored in MockAgent)

        Returns:
            Tuple of (response_text, list_of_tool_calls)
        """
        tool_calls: list[ToolCallInfo] = []

        # Get last user message
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break

        # T032: Handle empty message
        if not last_message.strip():
            return (
                "[Demo Mode] Please type a command. "
                "Try 'Show my tasks' or 'Add [task name]'.",
                [],
            )

        # Parse command from message
        parsed = self._parse_command(last_message)

        # T033: Handle unrecognized command
        if parsed.command_type == "unknown":
            return self._get_help_message(), []

        # T034: Handle MCP connection with try/except
        try:
            # T010: Connect to MCP server via stdio
            server_params = StdioServerParameters(
                command="python",
                args=[self.mcp_server_path],
                env={**os.environ},
            )

            async with (
                stdio_client(server_params) as (read, write),
                ClientSession(read, write) as mcp_session,
            ):
                await mcp_session.initialize()

                # Route to appropriate handler based on command type
                result_text = ""

                # T012: Handle 'add' command
                if parsed.command_type == "add":
                    if not parsed.task_title:
                        return (
                            "[Demo Mode] Please specify a task title. "
                            "Example: 'Add buy groceries'",
                            [],
                        )
                    result_text, tool_call = await self._call_add_task(
                        mcp_session, user_id, parsed.task_title
                    )
                    tool_calls.append(tool_call)

                # T016: Handle 'list' command
                elif parsed.command_type == "list":
                    result_text, tool_call = await self._call_list_tasks(
                        mcp_session, user_id, parsed.status_filter
                    )
                    tool_calls.append(tool_call)

                # T020: Handle 'complete' command
                elif parsed.command_type == "complete":
                    # T021: Handle missing UUID
                    if not parsed.task_id:
                        return (
                            "[Demo Mode] I need the task ID to complete it. "
                            "Try 'Show my tasks' first, then copy the task ID.",
                            [],
                        )
                    result_text, tool_call = await self._call_complete_task(
                        mcp_session, user_id, parsed.task_id
                    )
                    tool_calls.append(tool_call)

                # T024: Handle 'delete' command
                elif parsed.command_type == "delete":
                    # T025: Handle missing UUID
                    if not parsed.task_id:
                        return (
                            "[Demo Mode] I need the task ID to delete it. "
                            "Try 'Show my tasks' first, then copy the task ID.",
                            [],
                        )
                    result_text, tool_call = await self._call_delete_task(
                        mcp_session, user_id, parsed.task_id
                    )
                    tool_calls.append(tool_call)

                # T029: Handle 'update' command
                elif parsed.command_type == "update":
                    # T030: Handle missing UUID or title
                    if not parsed.task_id:
                        return (
                            "[Demo Mode] I need the task ID to update it. "
                            "Try 'Show my tasks' first, then copy the task ID.",
                            [],
                        )
                    if not parsed.new_title:
                        return (
                            "[Demo Mode] I need the new title. "
                            "Example: 'Update task [id] to Buy fruits'",
                            [],
                        )
                    result_text, tool_call = await self._call_update_task(
                        mcp_session, user_id, parsed.task_id, parsed.new_title
                    )
                    tool_calls.append(tool_call)

                # T014, T018: Format response with Demo Mode prefix
                return f"[Demo Mode] {result_text}", tool_calls

        except Exception as e:
            # T034: Handle MCP connection failure gracefully
            error_msg = str(e)
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                return (
                    "[Demo Mode] Service temporarily unavailable. "
                    "Please try again in a moment.",
                    [],
                )
            # T035: Pass through other errors
            return f"[Demo Mode] An error occurred: {error_msg}", []


def get_agent() -> TodoAgent | MockTodoAgent:
    """Factory function to get the appropriate agent.

    Returns MockTodoAgent if OpenAI API key is not configured.
    """
    settings = get_settings()

    if not settings.openai_api_key:
        return MockTodoAgent()

    return TodoAgent(settings.openai_api_key)
