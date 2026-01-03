"""Pydantic schemas for chat functionality."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID. If None, creates new conversation.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message to send to the chatbot.",
    )


class ToolCallInfo(BaseModel):
    """Information about a tool call made during the conversation."""

    tool_name: str
    arguments: dict
    result: str


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: UUID
    response: str
    tool_calls: list[ToolCallInfo] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Schema for a single message in conversation history."""

    id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    """Schema for conversation with messages."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Schema for list of conversations."""

    conversations: list[ConversationResponse]
    total: int
