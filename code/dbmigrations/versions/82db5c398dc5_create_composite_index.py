"""create composite index

Revision ID: 82db5c398dc5
Revises: 8e6844d0d977
Create Date: 2023-10-18 18:49:48.772121

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "82db5c398dc5"
down_revision = "8e6844d0d977"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("idx_users_apikey", "users", ["apikey"])
    op.create_index("idx_users_role_apikey", "users", ("role", "apikey"))
    op.create_index("idx_farm_id_user_id", "farm", ("id", "user_id"))


def downgrade() -> None:
    op.drop_index("idx_users_apikey")
    op.drop_index("idx_users_role_apikey")
    op.drop_index("idx_farm_id_user_id")
