"""add cloud cover to satellite table

Revision ID: 7dd5090e2f3c
Revises: 116a85962c8f
Create Date: 2022-12-14 15:27:26.465618

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7dd5090e2f3c"
down_revision = "116a85962c8f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "satellite",
        sa.Column("cloud_cover", sa.Boolean(), nullable=False, server_default="FALSE"),
    )


def downgrade() -> None:
    op.drop_column("satellite", "cloud_cover")
