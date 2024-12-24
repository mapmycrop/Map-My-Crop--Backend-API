"""payment table

Revision ID: 825f90c4d926
Revises: e579632e383a
Create Date: 2023-09-07 17:01:52.889228

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = "825f90c4d926"
down_revision = "e579632e383a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("farm_ids", sa.ARRAY(sa.String), nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("service", sa.String, nullable=False),
        sa.Column("payment_request", JSON, nullable=True),
        sa.Column("payment_response", JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("payments")
