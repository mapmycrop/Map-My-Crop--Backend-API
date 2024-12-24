"""create reseller and user_referral table

Revision ID: cd149e9a3a50
Revises: 6469663d506f
Create Date: 2024-03-12 00:03:53.910202

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cd149e9a3a50"
down_revision = "6469663d506f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "resellers",
        sa.Column("id", sa.Integer(), nullable=False, index=True),
        sa.Column("brand_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("gst_number", sa.String(), nullable=True),
        sa.Column("ref_code", sa.String(), unique=True, nullable=True),
        sa.Column("revenue", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("activated_at", sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user_referral",
        sa.Column("id", sa.Integer(), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), nullable=False, index=True),
        sa.Column("ref_code", sa.String(), nullable=True),
        sa.Column(
            "registered_at",
            sa.TIMESTAMP(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["ref_code"],
            ["resellers.ref_code"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("user_referral")
    op.drop_table("resellers")
