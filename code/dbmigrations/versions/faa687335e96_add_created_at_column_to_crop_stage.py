"""add created_at column to crop_stage

Revision ID: faa687335e96
Revises: 040e8148267d
Create Date: 2023-02-09 13:09:13.895023

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "faa687335e96"
down_revision = "040e8148267d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "farm_crop",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("farm_crop", "created_at")
