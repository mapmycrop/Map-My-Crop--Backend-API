"""add region field to farm table

Revision ID: 6469663d506f
Revises: 9f8932437b8b
Create Date: 2024-02-28 01:10:05.145755

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6469663d506f"
down_revision = "9f8932437b8b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("farm", sa.Column("region", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("farm", "region")
