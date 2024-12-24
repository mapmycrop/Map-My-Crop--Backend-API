"""create_growth_advisory_table

Revision ID: 765003d8cfa1
Revises: 1261e0c31d79
Create Date: 2023-08-21 03:46:42.036839

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "765003d8cfa1"
down_revision = "1261e0c31d79"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_growth_stage_advisories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("crop_id", sa.String(), nullable=False),
        sa.Column("stage", sa.String()),
        sa.Column("advisory", sa.String()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["crop_id"], ["crop.id"]),
    )


def downgrade() -> None:
    op.drop_table("crop_growth_stage_advisories")
