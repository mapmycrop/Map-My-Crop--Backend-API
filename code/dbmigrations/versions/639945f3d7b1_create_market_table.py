"""create market table

Revision ID: 639945f3d7b1
Revises: faa687335e96
Create Date: 2023-02-11 13:25:07.534956

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "639945f3d7b1"
down_revision = "faa687335e96"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market",
        sa.Column("state", sa.String()),
        sa.Column("district", sa.String()),
        sa.Column("market", sa.String()),
        sa.Column("commodity", sa.String()),
        sa.Column("variety", sa.String()),
        sa.Column("grade", sa.String()),
        sa.Column("arrival_date", sa.Date(), nullable=False),
        sa.Column("min_price", sa.Float()),
        sa.Column("max_price", sa.Float()),
        sa.Column("modal_price", sa.Float()),
        sa.Column(
            "updated_date",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "state",
            "district",
            "market",
            "commodity",
            "variety",
            "grade",
            "arrival_date",
            "min_price",
            "max_price",
            "modal_price",
            "updated_date",
        ),
    )


def downgrade() -> None:
    op.drop_table("market")
