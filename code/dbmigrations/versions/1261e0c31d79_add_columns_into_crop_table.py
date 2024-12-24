"""add_columns_into_crop_table

Revision ID: 1261e0c31d79
Revises: 7053727d0955
Create Date: 2023-08-17 04:33:44.716761

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1261e0c31d79"
down_revision = "7053727d0955"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crop", sa.Column("crop_from", sa.String(), nullable=True))
    op.add_column("crop", sa.Column("germination", sa.Integer(), nullable=True))
    op.add_column("crop", sa.Column("seedling", sa.Integer(), nullable=True))
    op.add_column("crop", sa.Column("vegetative_growth", sa.Integer(), nullable=True))
    op.add_column("crop", sa.Column("flowering", sa.Integer(), nullable=True))
    op.add_column("crop", sa.Column("fruiting", sa.Integer(), nullable=True))
    op.add_column("crop", sa.Column("maturity", sa.Integer(), nullable=True))
    op.add_column("crop", sa.Column("harvesting", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("crop", "crop_from")
    op.drop_column("crop", "germination")
    op.drop_column("crop", "seedling")
    op.drop_column("crop", "vegetative_growth")
    op.drop_column("crop", "flowering")
    op.drop_column("crop", "fruiting")
    op.drop_column("crop", "maturity")
    op.drop_column("crop", "harvesting")
