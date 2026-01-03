"""TodoAgent - AI agent for task management using OpenAI and MCP.

This agent connects to the MCP server to execute task operations
based on natural language user requests.
"""

import json
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

from src.config import get_settings
from src.schemas.chat import ToolCallInfo

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

    def _convert_mcp_tools_to_openai(
        self, mcp_tools: list[Any]
    ) -> list[dict]:
        """Convert MCP tool definitions to OpenAI function format."""
        openai_tools = []
        for tool in mcp_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            })
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

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    })

                # Add assistant message and tool results to conversation
                full_messages.append({
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
                })
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
    """Mock agent for testing without OpenAI API key."""

    async def run(
        self,
        user_id: str,  # noqa: ARG002
        messages: list[dict[str, str]],
        model: str = "gpt-4o-mini",  # noqa: ARG002
    ) -> tuple[str, list[ToolCallInfo]]:
        """Return a mock response for testing."""
        last_message = messages[-1]["content"] if messages else ""

        # Simple keyword-based mock responses
        response = (
            "I'm a mock todo assistant. To enable full AI functionality, "
            f"please set your OPENAI_API_KEY environment variable. "
            f"You said: '{last_message}'"
        )

        return response, []


def get_agent() -> TodoAgent | MockTodoAgent:
    """Factory function to get the appropriate agent.

    Returns MockTodoAgent if OpenAI API key is not configured.
    """
    settings = get_settings()

    if not settings.openai_api_key:
        return MockTodoAgent()

    return TodoAgent(settings.openai_api_key)
