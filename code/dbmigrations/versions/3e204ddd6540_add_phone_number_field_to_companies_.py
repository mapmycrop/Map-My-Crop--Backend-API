"""add phone number field to companies table

Revision ID: 3e204ddd6540
Revises: b4b0632c1316
Create Date: 2024-05-05 22:09:00.344840

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e204ddd6540"
down_revision = "b4b0632c1316"
branch_labels = None
depends_on = None

table_name = "companies"


def upgrade() -> None:
    op.add_column(table_name, sa.Column("ph", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column(table_name, "ph")
