"""farm dileanation

Revision ID: a11ee8b67a6c
Revises: b71788e14ca6
Create Date: 2023-02-27 08:28:35.329984

"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = "a11ee8b67a6c"
down_revision = "b71788e14ca6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farm_delineation",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("seeded_area", sa.Float()),
        sa.Column("area", sa.Float()),
        sa.Column("stileid", sa.String()),
        sa.Column("dates", sa.ARRAY(sa.Date)),
        sa.Column("country", sa.String()),
        sa.Column("vension", sa.String()),
        sa.Column("cluids", sa.ARRAY(sa.String)),
        sa.Column("flatness", sa.Float()),
        sa.Column("perimeter", sa.Float()),
        sa.Column("confidence", sa.Float()),
        sa.Column("state", sa.String()),
        sa.Column("json", sa.JSON()),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="POLYGON",
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("farm_delineation")
