"""empty message

Revision ID: 05b11f925f4a
Revises: 0c0e94b46ca4, 7dd5090e2f3c, dca81a47e6f3
Create Date: 2023-02-07 01:15:05.629322

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "05b11f925f4a"
down_revision = ("0c0e94b46ca4", "7dd5090e2f3c", "dca81a47e6f3")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
