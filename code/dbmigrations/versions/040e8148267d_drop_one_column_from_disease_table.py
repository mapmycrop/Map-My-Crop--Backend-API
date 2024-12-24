"""drop_one_column_from_disease_table

Revision ID: 040e8148267d
Revises: 870b41f4fe96
Create Date: 2023-02-08 03:42:31.182841

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "040e8148267d"
down_revision = "870b41f4fe96"
branch_labels = None
depends_on = None
table_name = "disease"


def upgrade() -> None:
    op.drop_column("disease", "scientific_name")


def downgrade() -> None:
    pass
