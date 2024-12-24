"""remove_constraint_from_advisory_table

Revision ID: e9d1922fe2c5
Revises: 108192d70b0d
Create Date: 2023-04-17 00:14:56.836809

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e9d1922fe2c5"
down_revision = "108192d70b0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        table_name="advisory", type_="foreignkey", constraint_name="advisory_crop_fkey"
    )


def downgrade() -> None:
    pass
