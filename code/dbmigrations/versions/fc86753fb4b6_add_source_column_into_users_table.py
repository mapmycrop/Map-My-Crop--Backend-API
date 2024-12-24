"""add_source_column_into_users_table

Revision ID: fc86753fb4b6
Revises: 825f90c4d926
Create Date: 2023-09-18 01:48:39.533113

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fc86753fb4b6"
down_revision = "825f90c4d926"
branch_labels = None
depends_on = None
table_name = "users"


def upgrade() -> None:
    source = ("Web", "Mobile")
    register_source = sa.Enum(*source, name="register_source")
    register_source.create(op.get_bind(), checkfirst=False)
    op.add_column(
        table_name,
        sa.Column(
            "source",
            sa.Enum("Web", "Mobile", name="register_source"),
            nullable=True,
            server_default="Web",
        ),
    )


def downgrade() -> None:
    op.drop_column(table_name, "source")
