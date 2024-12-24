"""add_is_active_to_company_table

Revision ID: 242644bb2493
Revises: 9acd7937db4c
Create Date: 2023-05-12 03:22:09.805871

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "242644bb2493"
down_revision = "9acd7937db4c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "companies", sa.Column("is_active", sa.Boolean(), server_default="TRUE")
    )

    op.get_bind().execute(f"update companies set is_active = TRUE")


def downgrade() -> None:
    op.drop_column("companies", "is_active")
