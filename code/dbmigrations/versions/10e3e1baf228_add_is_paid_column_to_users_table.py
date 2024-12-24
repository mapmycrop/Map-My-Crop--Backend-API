"""add_is_paid_column_to_users_table

Revision ID: 10e3e1baf228
Revises: b596d8abf16d
Create Date: 2023-04-27 01:24:05.423712

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

from models import User

# revision identifiers, used by Alembic.
revision = "10e3e1baf228"
down_revision = "b596d8abf16d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_paid", sa.Boolean(), default=False))

    bind = op.get_bind()

    bind.execute(f"update users set is_paid = false")


def downgrade() -> None:
    op.drop_column("users", "is_paid")
