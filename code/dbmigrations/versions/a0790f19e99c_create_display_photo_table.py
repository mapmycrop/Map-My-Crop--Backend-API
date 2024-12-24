"""Create display_photo table

Revision ID: a0790f19e99c
Revises: 3b4a530a16b0
Create Date: 2024-06-06 19:48:45.559414

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0790f19e99c"
down_revision = "3b4a530a16b0"
branch_labels = None
depends_on = None

table_name = "display_photo"


def upgrade() -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("path", sa.String, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=False),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table(table_name)
