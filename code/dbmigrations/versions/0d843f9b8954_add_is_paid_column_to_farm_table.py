"""add_is_paid_column_to_farm_table

Revision ID: 0d843f9b8954
Revises: 8a86006ed4d1
Create Date: 2023-05-09 04:40:11.306148

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0d843f9b8954"
down_revision = "8a86006ed4d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("farm", sa.Column("is_paid", sa.Boolean(), default=False))

    bind = op.get_bind()

    bind.execute(f"update farm set is_paid = false")


def downgrade() -> None:
    op.drop_column("farm", "is_paid")
