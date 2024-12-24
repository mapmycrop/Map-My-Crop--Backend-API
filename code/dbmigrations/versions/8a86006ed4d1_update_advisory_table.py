"""update_advisory_table

Revision ID: 8a86006ed4d1
Revises: 41f5f532d284
Create Date: 2023-05-08 02:53:01.615686

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8a86006ed4d1"
down_revision = "41f5f532d284"
branch_labels = None
depends_on = None

table_name = "advisory"


def upgrade() -> None:
    op.alter_column(
        table_name, column_name="stage_growth", new_column_name="advisory_title"
    )
    op.alter_column(table_name, column_name="advisory", new_column_name="advisory_desc")
    op.add_column(table_name, sa.Column("stage_growth", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column(table_name, "stage_growth")
    op.alter_column(table_name, column_name="advisory_desc", new_column_name="advisory")
    op.alter_column(
        table_name, column_name="advisory_title", new_column_name="stage_growth"
    )
