"""create_crop_guide_table

Revision ID: e8adfea90e7f
Revises: faa687335e96
Create Date: 2023-02-10 00:04:51.542385

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e8adfea90e7f"
down_revision = "faa687335e96"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_guide",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("link", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("crop_guide")
