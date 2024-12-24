"""update user and company table

Revision ID: 9f8932437b8b
Revises: 7fff6ab90c31
Create Date: 2024-02-07 03:15:29.621138

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f8932437b8b"
down_revision = "7fff6ab90c31"
branch_labels = None
depends_on = None

user_tbl = "users"
company_tbl = "companies"


def upgrade() -> None:

    unit_score_list = ("metric", "imperial")

    unit_score = sa.Enum(*unit_score_list, name="unit_score")
    unit_score.create(op.get_bind(), checkfirst=False)

    op.add_column(user_tbl, sa.Column("country", sa.String(), nullable=True))
    op.add_column(user_tbl, sa.Column("city", sa.String(), nullable=True))
    op.add_column(user_tbl, sa.Column("state", sa.String(), nullable=True))
    op.add_column(user_tbl, sa.Column("postcode", sa.String(), nullable=True))
    op.add_column(company_tbl, sa.Column("city", sa.String(), nullable=True))
    op.add_column(company_tbl, sa.Column("state", sa.String(), nullable=True))
    op.add_column(company_tbl, sa.Column("postcode", sa.String(), nullable=True))
    unit_type_enum = sa.Enum("metric", "imperial", name="unit_source")
    unit_type_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        user_tbl,
        sa.Column(
            "unit",
            unit_type_enum,
            nullable=False,
            server_default="metric",
        ),
    )
    op.add_column(
        company_tbl,
        sa.Column(
            "unit",
            unit_type_enum,
            nullable=False,
            server_default="metric",
        ),
    )


def downgrade() -> None:
    op.drop_column(user_tbl, "country")
    op.drop_column(user_tbl, "city")
    op.drop_column(user_tbl, "state")
    op.drop_column(user_tbl, "unit")
    op.drop_column(user_tbl, "postcode")
    op.drop_column(company_tbl, "city")
    op.drop_column(company_tbl, "state")
    op.drop_column(company_tbl, "unit")
    op.drop_column(company_tbl, "postcode")
