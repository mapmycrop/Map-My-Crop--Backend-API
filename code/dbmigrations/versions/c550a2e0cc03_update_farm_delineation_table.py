"""update farm_delineation table

Revision ID: c550a2e0cc03
Revises: a11ee8b67a6c
Create Date: 2023-03-02 08:22:33.380305

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c550a2e0cc03"
down_revision = "a11ee8b67a6c"
branch_labels = None
depends_on = None

TABLE_NAME = "farm_delineation"


def upgrade() -> None:
    op.alter_column(TABLE_NAME, "vension", new_column_name="version")
    op.add_column(TABLE_NAME, sa.Column("old_id", sa.String()))


def downgrade() -> None:
    op.alter_column(TABLE_NAME, "version", new_column_name="vension")
    op.drop_column(TABLE_NAME, "old_id")
