"""add_created_at_column_into_contacts_table

Revision ID: f87b4633170b
Revises: d60d9a01f973
Create Date: 2023-06-15 05:42:21.861777

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f87b4633170b"
down_revision = "d60d9a01f973"
branch_labels = None
depends_on = None

table_name = "contacts"


def upgrade() -> None:
    op.add_column(table_name, sa.Column("title", sa.String()))
    op.add_column(table_name, sa.Column("created_at", sa.DateTime()))
    op.add_column(table_name, sa.Column("user_id", sa.Integer()))
    op.drop_column(table_name, "email")
    op.drop_column(table_name, "phone")
    sa.ForeignKeyConstraint(["user_id"], ["users.id"]),


def downgrade() -> None:
    op.drop_column(table_name, "title")
    op.drop_column(table_name, "created_at")
    op.drop_column(table_name, "user_id")
    op.add_column(table_name, sa.Column("email", sa.String(), nullable=True))
    op.add_column(table_name, sa.Column("phone", sa.String(), nullable=False))
