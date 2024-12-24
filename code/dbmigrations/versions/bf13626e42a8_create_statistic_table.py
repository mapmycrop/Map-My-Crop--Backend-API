"""create_statistic_table

Revision ID: bf13626e42a8
Revises: 84bed176ab11
Create Date: 2023-04-10 07:19:15.909249

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bf13626e42a8"
down_revision = "84bed176ab11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "statistic",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farmers_count", sa.Integer(), nullable=False),
        sa.Column("total_farms_mapped", sa.Integer(), nullable=False),
        sa.Column("active_users", sa.Integer(), nullable=False),
        sa.Column("non_active_users", sa.Integer(), nullable=False),
        sa.Column("paying_farmers", sa.Integer(), nullable=False),
        sa.Column("non_paying_farmers", sa.Integer(), nullable=False),
        sa.Column("enterprise_users", sa.Integer(), nullable=False),
        sa.Column("countrywise_farmers", sa.Integer(), nullable=False),
        sa.Column("api_keys", sa.Integer(), nullable=False),
        sa.Column("scouting_total", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("statistic")
