"""update_fertilize_table

Revision ID: dca81a47e6f3
Revises: 13e09d720af6
Create Date: 2023-01-27 09:55:00.270311

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dca81a47e6f3"
down_revision = "13e09d720af6"
branch_labels = None
depends_on = None

table_name = "fertilizers"


def upgrade() -> None:
    op.alter_column(
        table_name=table_name,
        column_name="crop",
        new_column_name="crop_id",
    )
    op.create_foreign_key(
        constraint_name="fertilizer_crop",
        source_table=table_name,
        referent_table="crop",
        local_cols=["crop_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_column(table_name=table_name, column_name="crop_id")
