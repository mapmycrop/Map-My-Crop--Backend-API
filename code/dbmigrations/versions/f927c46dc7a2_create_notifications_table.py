"""create_notifications_table

Revision ID: f927c46dc7a2
Revises: 6d72fb9adfcd
Create Date: 2024-07-24 16:38:29.849747

"""

import uuid
from uuid import UUID
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "f927c46dc7a2"
down_revision = "6d72fb9adfcd"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            default=uuid.uuid4,
            primary_key=True,
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.String(), nullable=True),
        sa.Column(
            "status", sa.String(), nullable=True, server_default=sa.text("'created'")
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("attachments", sa.JSON(), nullable=True),
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.sql.expression.false(),
        ),
        sa.Column(
            "created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("delivered_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("read_at", sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )


def downgrade():
    op.drop_table("notifications")
