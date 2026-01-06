"""Conversation service for chat operations."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.conversation import Conversation, Message
from src.schemas.chat import ConversationResponse, MessageResponse


class ConversationService:
    """Service for conversation and message operations."""

    def __init__(self, session: AsyncSession, user_id: UUID) -> None:
        self.session = session
        self.user_id = user_id

    async def create_conversation(self) -> Conversation:
        """Create a new conversation for the user."""
        conversation = Conversation(user_id=self.user_id)
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        """Get a conversation by ID for the current user."""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == self.user_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_or_create_conversation(
        self, conversation_id: UUID | None
    ) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id:
            conversation = await self.get_conversation(conversation_id)
            if conversation:
                return conversation
        return await self.create_conversation()

    async def get_messages(self, conversation_id: UUID) -> list[Message]:
        """Get all messages for a conversation, ordered by creation time."""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls_json: str | None = None,
    ) -> Message:
        """Add a message to a conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls_json=tool_calls_json,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)

        # Update conversation timestamp
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(UTC)
            await self.session.flush()

        return message

    async def get_message_history_for_agent(
        self, conversation_id: UUID, max_messages: int = 20
    ) -> list[dict[str, str]]:
        """Get message history formatted for OpenAI agent.

        Returns list of {"role": "user"|"assistant", "content": "..."} dicts.
        Limits to most recent messages to avoid token limits.
        """
        messages = await self.get_messages(conversation_id)

        # Take last N messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        return [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]

    async def list_conversations(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[ConversationResponse], int]:
        """List all conversations for the user."""
        # Count total
        from sqlalchemy import func

        count_query = select(func.count()).select_from(
            select(Conversation)
            .where(Conversation.user_id == self.user_id)
            .subquery()
        )
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        query = (
            select(Conversation)
            .where(Conversation.user_id == self.user_id)
            .order_by(Conversation.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.session.execute(query)
        conversations = result.scalars().all()

        # Build response with messages
        responses = []
        for conv in conversations:
            messages = await self.get_messages(conv.id)
            responses.append(
                ConversationResponse(
                    id=conv.id,
                    user_id=conv.user_id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    messages=[
                        MessageResponse(
                            id=msg.id,
                            role=msg.role,
                            content=msg.content,
                            created_at=msg.created_at,
                        )
                        for msg in messages[:5]  # Limit preview messages
                    ],
                )
            )

        return responses, total

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """Delete a conversation and all its messages."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False

        await self.session.delete(conversation)
        await self.session.flush()
        return True
