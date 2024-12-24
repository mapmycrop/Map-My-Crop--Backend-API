"""set SRID on farm_delineation

Revision ID: 8e6844d0d977
Revises: 737b30e18c5e
Create Date: 2023-10-16 21:12:47.067838

"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


# revision identifiers, used by Alembic.
revision = "8e6844d0d977"
down_revision = "737b30e18c5e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "farm_delineation",
        "geometry",
        type_=Geometry(
            geometry_type="POLYGON",
            spatial_index=False,
            from_text="ST_GeomFromEWKT",
            name="geometry",
            srid=4326,
        ),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "farm_delineation",
        "geometry",
        type_=Geometry(
            geometry_type="POLYGON",
            spatial_index=False,
            from_text="ST_GeomFromEWKT",
            name="geometry",
        ),
        nullable=False,
    )
