"""create_feedback_table

Revision ID: ab81afcb06d5
Revises: d33629adeff9
Create Date: 2023-01-17 00:27:55.539543

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ab81afcb06d5"
down_revision = "d33629adeff9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("feedback")
