"""create_columns_into_farm_crop_table

Revision ID: 737b30e18c5e
Revises: c59724261179
Create Date: 2023-10-06 06:06:26.452007

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "737b30e18c5e"
down_revision = "c59724261179"
branch_labels = None
depends_on = None


def upgrade() -> None:
    maturity = ("early", "mid", "late")

    farm_crop_maturity = sa.Enum(*maturity, name="farm_crop_maturity")
    farm_crop_maturity.create(op.get_bind(), checkfirst=False)

    op.add_column(
        "farm_crop",
        sa.Column(
            "maturity",
            sa.Enum(*maturity, name="farm_crop_maturity"),
            server_default="early",
        ),
    )

    irrigation_type = (
        "center pivot",
        "drip",
        "horse end",
        "sprinkler",
        "micro",
        "canal",
        "borewell",
        "other",
    )

    farm_crop_irrigation_type = sa.Enum(
        *irrigation_type, name="farm_crop_irrigation_type"
    )
    farm_crop_irrigation_type.create(op.get_bind(), checkfirst=False)

    op.add_column(
        "farm_crop",
        sa.Column(
            "irrigation_type",
            sa.Enum(*irrigation_type, name="farm_crop_irrigation_type"),
            server_default="center pivot",
        ),
    )

    tillage_type = ("no till", "intense", "conservation")

    farm_crop_tillage_type = sa.Enum(*tillage_type, name="farm_crop_tillage_type")
    farm_crop_tillage_type.create(op.get_bind(), checkfirst=False)

    op.add_column(
        "farm_crop",
        sa.Column(
            "tillage_type",
            sa.Enum(*tillage_type, name="farm_crop_tillage_type"),
            server_default="no till",
        ),
    )

    op.add_column("farm_crop", sa.Column("target_yield", sa.Integer(), nullable=True))
    op.add_column("farm_crop", sa.Column("actual_yield", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("farm_crop", "maturity")
    op.drop_column("farm_crop", "irrigation_type")
    op.drop_column("farm_crop", "tillage_type")
    op.drop_column("farm_crop", "target_yield")
    op.drop_column("farm_crop", "actual_yield")
