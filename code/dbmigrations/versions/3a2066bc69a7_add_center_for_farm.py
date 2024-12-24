"""add center for farm

Revision ID: 3a2066bc69a7
Revises: 4985b8d8553d
Create Date: 2023-05-28 20:54:23.631883

"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = "3a2066bc69a7"
down_revision = "4985b8d8553d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # op.execute(
    #     """ALTER TABLE farm ADD COLUMN center geometry(Point, 4326) GENERATED ALWAYS AS (ST_Centroid(geometry)) STORED;"""
    # )

    op.add_column(
        "farm",
        sa.Column(
            "center",
            Geometry(geometry_type="POINT", srid=4326),
            sa.Computed(
                "(ST_Centroid(geometry))",
                True,
            ),
        ),
    )


def downgrade() -> None:
    op.drop_column("farm", "center")
