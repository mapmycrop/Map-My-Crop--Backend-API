"""create expiry date in farm table

Revision ID: b4b0632c1316
Revises: b9ea97563998
Create Date: 2024-05-01 17:12:07.474456

"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta


# revision identifiers, used by Alembic.
revision = "b4b0632c1316"
down_revision = "b9ea97563998"
branch_labels = None
depends_on = None

table_name = "farm"


def upgrade() -> None:
    op.add_column(table_name, sa.Column("expiry_date", sa.DateTime(), nullable=True))

    current_date = datetime.now()
    # expiry_date = current_date + timedelta(days=365)
    expiry_date = "2099-12-31"

    # Update the expiry_date column for all existing rows in the 'farm' table
    conn = op.get_bind()
    conn.execute(f"UPDATE {table_name} SET expiry_date = %s", (expiry_date,))


def downgrade() -> None:
    op.drop_column(table_name, "expiry_date")
