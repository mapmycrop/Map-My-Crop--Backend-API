"""update user table with is_delete_field

Revision ID: 28ec6b5f2ba7
Revises: 386f2e9853d0
Create Date: 2024-01-23 22:59:50.238151

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "28ec6b5f2ba7"
down_revision = "386f2e9853d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_deleted", sa.Boolean(), default=False))
    pass


def downgrade() -> None:
    op.drop_column("users", "is_deleted")
    pass
