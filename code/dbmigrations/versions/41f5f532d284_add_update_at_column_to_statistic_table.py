"""add_update_at_column_to_statistic_table

Revision ID: 41f5f532d284
Revises: 1e974387109a
Create Date: 2023-05-05 01:35:53.380227

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "41f5f532d284"
down_revision = "1e974387109a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "statistic",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("statistic", "updated_at")
