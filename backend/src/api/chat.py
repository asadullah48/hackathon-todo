"""Chat API endpoints for AI-powered task management."""

import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.agents.todo_agent import get_agent
from src.api.deps import CurrentUserDep, SessionDep
from src.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
)
from src.services.conversation import ConversationService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ChatResponse:
    """Send a message to the AI chatbot and get a response.

    This endpoint is stateless - conversation state is stored in the database.
    Each request loads conversation history, calls the AI agent, and saves the response.

    Args:
        request: ChatRequest with optional conversation_id and message
        session: Database session
        current_user_id: Authenticated user's UUID

    Returns:
        ChatResponse with conversation_id, AI response, and tool call info
    """
    conversation_service = ConversationService(session, current_user_id)

    # Get or create conversation
    conversation = await conversation_service.get_or_create_conversation(
        request.conversation_id
    )

    # Load conversation history for agent
    messages = await conversation_service.get_message_history_for_agent(
        conversation.id
    )

    # Add the new user message
    messages.append({"role": "user", "content": request.message})

    # Store user message in database
    await conversation_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    # Run the AI agent
    try:
        agent = get_agent()
        response_text, tool_calls = await agent.run(
            user_id=str(current_user_id),
            messages=messages,
        )
    except ValueError as e:
        # Handle missing API key gracefully
        response_text = str(e)
        tool_calls = []
    except Exception as e:
        # Check if it's a rate limit/quota error - use mock agent
        # Use repr() to get full nested exception info for ExceptionGroups
        error_str = repr(e).lower()
        if "rate" in error_str or "quota" in error_str or "429" in error_str:
            # Fallback to mock agent for quota issues
            from src.agents.todo_agent import MockTodoAgent
            mock_agent = MockTodoAgent()
            response_text, tool_calls = await mock_agent.run(
                user_id=str(current_user_id),
                messages=messages,
            )
            response_text = (
                "⚠️ OpenAI API quota exceeded. Using demo mode.\n\n"
                + response_text
            )
        else:
            # Log the error for debugging
            import sys
            import traceback
            print(f"Agent error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            response_text = (
                "I encountered an error processing your request. "
                "Please try again or rephrase your request."
            )
            tool_calls = []

    # Store assistant response in database
    await conversation_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        tool_calls_json=json.dumps([tc.model_dump() for tc in tool_calls]) if tool_calls else None,
    )

    return ChatResponse(
        conversation_id=conversation.id,
        response=response_text,
        tool_calls=tool_calls,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    session: SessionDep,
    current_user_id: CurrentUserDep,
    page: int = 1,
    page_size: int = 20,
) -> ConversationListResponse:
    """List all conversations for the current user.

    Args:
        session: Database session
        current_user_id: Authenticated user's UUID
        page: Page number (1-indexed)
        page_size: Number of conversations per page

    Returns:
        ConversationListResponse with paginated conversations
    """
    conversation_service = ConversationService(session, current_user_id)
    conversations, total = await conversation_service.list_conversations(
        page=page,
        page_size=page_size,
    )

    return ConversationListResponse(
        conversations=conversations,
        total=total,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> ConversationResponse:
    """Get a specific conversation with all messages.

    Args:
        conversation_id: UUID of the conversation
        session: Database session
        current_user_id: Authenticated user's UUID

    Returns:
        ConversationResponse with full message history

    Raises:
        HTTPException 404 if conversation not found
    """
    conversation_service = ConversationService(session, current_user_id)
    conversation = await conversation_service.get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await conversation_service.get_messages(conversation_id)

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    session: SessionDep,
    current_user_id: CurrentUserDep,
) -> None:
    """Delete a conversation and all its messages.

    Args:
        conversation_id: UUID of the conversation to delete
        session: Database session
        current_user_id: Authenticated user's UUID

    Raises:
        HTTPException 404 if conversation not found
    """
    conversation_service = ConversationService(session, current_user_id)
    deleted = await conversation_service.delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
