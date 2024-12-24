"""add_status_column_into_scouting

Revision ID: c7a85bc383a9
Revises: dfe89b3a8e9f
Create Date: 2023-07-14 04:46:29.020100

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7a85bc383a9"
down_revision = "dfe89b3a8e9f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    status = ("open", "in progress", "closed")

    scouting_status = sa.Enum(*status, name="scouting_status")
    scouting_status.create(op.get_bind(), checkfirst=False)

    op.add_column(
        "scoutings",
        sa.Column(
            "status", sa.Enum(*status, name="scouting_status"), server_default="open"
        ),
    )


def downgrade() -> None:
    op.drop_column("scoutings", "status")
    op.execute("Drop type scouting_status")
