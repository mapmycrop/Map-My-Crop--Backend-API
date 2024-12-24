"""add_name_column_into_users_table

Revision ID: 910675aa0bc3
Revises: 71cd5718cb5d
Create Date: 2023-08-10 02:36:55.854864

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "910675aa0bc3"
down_revision = "71cd5718cb5d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("name", sa.String(), nullable=False, server_default="")
    )


def downgrade() -> None:
    op.drop_column("users", "name")
