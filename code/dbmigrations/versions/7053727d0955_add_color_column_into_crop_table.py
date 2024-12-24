"""add_color_column_into_crop_table

Revision ID: 7053727d0955
Revises: d93e1cc5d093
Create Date: 2023-08-16 02:26:54.192722

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7053727d0955"
down_revision = "d93e1cc5d093"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "crop",
        sa.Column("color", sa.String(), nullable=False, server_default="#000000"),
    )


def downgrade() -> None:
    op.drop_column("crop", "color")
