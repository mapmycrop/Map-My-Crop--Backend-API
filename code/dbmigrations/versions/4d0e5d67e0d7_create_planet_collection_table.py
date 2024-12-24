"""create planet_collection table

Revision ID: 4d0e5d67e0d7
Revises: 18a923df07b8
Create Date: 2024-03-10 22:16:09.430980

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d0e5d67e0d7"
down_revision = "18a923df07b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "planet_collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farm_id", sa.String(), nullable=False),
        sa.Column("service_id", sa.String(), nullable=False),
        sa.Column("collection_id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("planet_collections")
