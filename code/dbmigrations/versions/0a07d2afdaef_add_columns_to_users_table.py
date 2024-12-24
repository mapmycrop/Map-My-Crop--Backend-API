"""add_columns_to_users_table

Revision ID: 0a07d2afdaef
Revises: a0790f19e99c
Create Date: 2024-07-24 16:30:14.612582

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0a07d2afdaef"
down_revision = "a0790f19e99c"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        "users",
        sa.Column(
            "timezone",
            sa.String(),
            nullable=False,
            default="Asia/Kolkata",
            server_default="Asia/Kolkata",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_notification_enabled",
            sa.Boolean(),
            nullable=False,
            default=False,
            server_default=sa.false(),
        ),
    )


def downgrade():

    op.drop_column("users", "is_notification_enabled")
    op.drop_column("users", "timezone")
