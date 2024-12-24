"""create scouting date

Revision ID: 7fff6ab90c31
Revises: 28ec6b5f2ba7
Create Date: 2024-02-05 00:02:40.159972

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7fff6ab90c31"
down_revision = "28ec6b5f2ba7"
branch_labels = None
depends_on = None

table_name = "scoutings"


def upgrade() -> None:
    op.add_column(table_name, sa.Column("created_at", sa.DateTime()))


def downgrade() -> None:
    op.drop_column(table_name, "created_at")
