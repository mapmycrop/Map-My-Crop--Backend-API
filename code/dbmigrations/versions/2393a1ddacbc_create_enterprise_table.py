"""create_enterprise_table

Revision ID: 2393a1ddacbc
Revises: c7a85bc383a9
Create Date: 2023-07-20 05:45:45.946312

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2393a1ddacbc"
down_revision = "c7a85bc383a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "enterprise_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("enterprise_id", sa.Integer(), nullable=False),
        sa.Column("total_farmers", sa.Integer()),
        sa.Column("total_farms", sa.Integer()),
        sa.Column("total_paid_farms", sa.Integer()),
        sa.Column("total_unpaid_farms", sa.Integer()),
        sa.Column("total_area", sa.Float()),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["enterprise_id"], ["companies.id"]),
    )


def downgrade() -> None:
    op.drop_table("enterprise_stats")
