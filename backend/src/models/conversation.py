"""Conversation and Message database models for chat functionality."""
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


class Conversation(SQLModel, table=True):
    """Conversation entity for chat sessions."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Relationship to messages
    messages: list["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message entity for chat messages."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # 'user', 'assistant', 'system'
    content: str = Field(default="")
    tool_calls_json: str | None = Field(default=None)  # JSON string for tool call metadata
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # Relationship to conversation
    conversation: Conversation | None = Relationship(back_populates="messages")
