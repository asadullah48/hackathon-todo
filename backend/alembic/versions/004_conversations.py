"""Add conversations and messages tables for chat functionality.

Revision ID: 004
Revises: 003
Create Date: 2026-01-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_conversations_user_id", "conversations", ["user_id"])

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("tool_calls_json", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index(
        "idx_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_messages_conversation_created", table_name="messages")
    op.drop_index("idx_messages_conversation_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("idx_conversations_user_id", table_name="conversations")
    op.drop_table("conversations")
