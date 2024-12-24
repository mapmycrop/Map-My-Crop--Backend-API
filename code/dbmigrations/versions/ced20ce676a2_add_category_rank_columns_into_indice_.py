"""add_category_rank_columns_into_indice_table

Revision ID: ced20ce676a2
Revises: da0eb5cef5eb
Create Date: 2023-08-04 03:21:31.093047

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ced20ce676a2"
down_revision = "da0eb5cef5eb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("indice", sa.Column("category", sa.String(), server_default="all"))
    op.add_column("indice", sa.Column("rank", sa.Integer()))


def downgrade() -> None:
    op.drop_column("indice", "category")
    op.drop_column("indice", "rank")
