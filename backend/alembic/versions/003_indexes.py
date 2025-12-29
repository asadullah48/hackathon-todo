"""Add performance indexes.

Revision ID: 003
Revises: 002
Create Date: 2025-12-28

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Index for filtering by completion status
    op.create_index(
        "idx_tasks_user_completed",
        "tasks",
        ["user_id", "is_completed"],
    )


def downgrade() -> None:
    op.drop_index("idx_tasks_user_completed", table_name="tasks")
