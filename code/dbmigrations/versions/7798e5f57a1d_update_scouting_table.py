"""update scouting table

Revision ID: 7798e5f57a1d
Revises: 3e204ddd6540
Create Date: 2024-05-08 15:46:23.598142

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7798e5f57a1d"
down_revision = "3e204ddd6540"
branch_labels = None
depends_on = None

table_name = "scoutings"


def upgrade() -> None:
    op.add_column(table_name, sa.Column("ground_notes", sa.String(), nullable=True))
    op.add_column(table_name, sa.Column("amount", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column(table_name, "ground_notes")
    op.drop_column(table_name, "amount")
