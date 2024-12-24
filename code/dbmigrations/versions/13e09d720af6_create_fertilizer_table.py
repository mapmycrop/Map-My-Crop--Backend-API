"""create_fertilizer_table

Revision ID: 13e09d720af6
Revises: ab81afcb06d5
Create Date: 2023-01-25 08:09:03.069804

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "13e09d720af6"
down_revision = "ab81afcb06d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fertilizers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("crop", sa.String(), nullable=False),
        sa.Column("urea", sa.Float(), nullable=False),
        sa.Column("ssp", sa.Float(), nullable=False),
        sa.Column("mop", sa.Float(), nullable=False),
        sa.Column("dap", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("fertilizers")
