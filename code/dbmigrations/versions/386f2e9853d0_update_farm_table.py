"""update farm table

Revision ID: 386f2e9853d0
Revises: 2c36e1347cea
Create Date: 2023-12-15 15:50:42.855257

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "386f2e9853d0"
down_revision = "2c36e1347cea"
branch_labels = None
depends_on = None
table_name = "farm"


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
    op.add_column(
        table_name,
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column(table_name, "created_at")
    op.drop_column(table_name, "updated_at")
