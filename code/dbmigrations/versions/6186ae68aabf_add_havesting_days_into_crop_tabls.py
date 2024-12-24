"""add_havesting_days_into_crop_tabls

Revision ID: 6186ae68aabf
Revises: dfe89b3a8e9f
Create Date: 2023-07-11 01:24:23.950075

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6186ae68aabf"
down_revision = "dfe89b3a8e9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crop", sa.Column("harvesting_days", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("crop", "harvesting_days")
