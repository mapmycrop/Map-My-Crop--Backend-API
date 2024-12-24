"""added_type_column_into_advisory_table

Revision ID: dfe89b3a8e9f
Revises: 931a4ba0ac1f
Create Date: 2023-07-05 01:21:55.011007

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dfe89b3a8e9f"
down_revision = "931a4ba0ac1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("advisory", sa.Column("type", sa.String()))


def downgrade() -> None:
    op.drop_column("advisory", "type")
