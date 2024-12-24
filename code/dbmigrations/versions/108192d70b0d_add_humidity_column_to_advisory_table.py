"""add_humidity_column_to_advisory_table

Revision ID: 108192d70b0d
Revises: d2814e6ad544
Create Date: 2023-04-14 02:41:14.534907

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "108192d70b0d"
down_revision = "d2814e6ad544"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("advisory", sa.Column("humidity_min", sa.Float()))
    op.add_column("advisory", sa.Column("humidity_max", sa.Float()))


def downgrade() -> None:
    op.drop_column("advisory", "humidity_max")
    op.drop_column("advisory", "humidity_min")
