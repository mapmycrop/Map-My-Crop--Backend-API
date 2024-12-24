"""add_crop_wise_column_into_enterprise_stas_table

Revision ID: c59724261179
Revises: fc86753fb4b6
Create Date: 2023-10-04 03:01:45.331649

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c59724261179"
down_revision = "fc86753fb4b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("enterprise_stats", sa.Column("crop_wise", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("enterprise_stats", "crop_wise")
