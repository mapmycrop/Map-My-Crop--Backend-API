"""update login_logs table

Revision ID: d673ed1afc40
Revises: 47b8114d6d81
Create Date: 2024-03-14 22:04:28.614916

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d673ed1afc40"
down_revision = "47b8114d6d81"
branch_labels = None
depends_on = None

table_name = "login_logs"


def upgrade() -> None:
    op.add_column(
        table_name, sa.Column("apikey", sa.String(), nullable=False, default="")
    )
    op.add_column(table_name, sa.Column("role", sa.Integer, nullable=False, default=""))


def downgrade() -> None:
    op.drop_column(table_name, "apikey")
    op.drop_column(table_name, "role")
