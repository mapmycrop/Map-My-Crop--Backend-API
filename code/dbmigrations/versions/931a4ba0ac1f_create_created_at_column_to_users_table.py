"""create_created_at_column_to_users_table

Revision ID: 931a4ba0ac1f
Revises: 3a2066bc69a7
Create Date: 2023-06-28 01:00:52.922557

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "931a4ba0ac1f"
down_revision = "3a2066bc69a7"
branch_labels = None
depends_on = None

table_name = "users"


def upgrade() -> None:
    op.add_column(
        table_name,
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.drop_column(table_name, "is_paid")


def downgrade() -> None:
    op.drop_column(table_name, "created_at")
    op.add_column(table_name, sa.Column("is_paid", sa.Boolean(), default=False))

    bind = op.get_bind()

    bind.execute(f"update users set is_paid = false")
