"""create invited user table

Revision ID: b6c3cd85fe2a
Revises: a0002ae28ae8
Create Date: 2024-04-21 19:09:58.773868

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b6c3cd85fe2a"
down_revision = "a0002ae28ae8"
branch_labels = None
depends_on = None

table_name = "invited_users"


def upgrade() -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ref_code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("mobile_number", sa.String(), nullable=False),
        sa.Column("paid_status", sa.Boolean(), nullable=False, default=False),
        sa.Column("farm_size", sa.Float(), nullable=True),
        sa.Column("crop_type", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ref_code"], ["resellers.ref_code"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table(table_name)
