"""create login log table

Revision ID: 47b8114d6d81
Revises: cd149e9a3a50
Create Date: 2024-03-13 23:39:16.412016

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "47b8114d6d81"
down_revision = "cd149e9a3a50"
branch_labels = None
depends_on = None

table_name = "login_logs"


def upgrade() -> None:
    logs_types = ("web", "android", "ios", "api")

    logs_type_enum = sa.Enum(*logs_types, name="logs_type")
    logs_type_enum.create(op.get_bind(), checkfirst=False)

    op.create_table(
        table_name,
        sa.Column("id", sa.Integer),
        sa.Column("ph", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column(
            "source",
            sa.Enum(*logs_types, name="logs_type"),
            nullable=False,
            server_default="web",
        ),
        sa.Column(
            "datetime", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table(table_name)
