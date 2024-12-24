"""empty message

Revision ID: da0eb5cef5eb
Revises: c7a85bc383a9, fe52c066238f, 92e7e2f41c85
Create Date: 2023-07-24 07:27:23.282259

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "da0eb5cef5eb"
down_revision = ("c7a85bc383a9", "fe52c066238f", "92e7e2f41c85")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
