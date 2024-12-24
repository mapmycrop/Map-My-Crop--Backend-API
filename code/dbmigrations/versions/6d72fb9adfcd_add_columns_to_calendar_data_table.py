"""add_columns_to_calendar_data_table

Revision ID: 6d72fb9adfcd
Revises: 0a07d2afdaef
Create Date: 2024-07-24 16:37:23.389705

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6d72fb9adfcd"
down_revision = "0a07d2afdaef"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.alter_column("calendar_data", "start_date", type_=sa.DateTime(), nullable=False)
    op.alter_column("calendar_data", "end_date", type_=sa.DateTime(), nullable=False)


def downgrade() -> None:

    op.alter_column("calendar_data", "start_date", type_=sa.Date(), nullable=False)
    op.alter_column("calendar_data", "end_date", type_=sa.Date(), nullable=False)
