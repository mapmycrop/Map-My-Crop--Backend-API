"""update_disease_table_nullable

Revision ID: 870b41f4fe96
Revises: eb75a982a37e
Create Date: 2023-02-07 04:33:29.932275

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "870b41f4fe96"
down_revision = "eb75a982a37e"
branch_labels = None
depends_on = None
table_name = "disease"


def upgrade() -> None:
    op.drop_column(table_name, "pre")
    op.drop_column(table_name, "folder_name")
    op.drop_column(table_name, "file_format")
    op.drop_column(table_name, "affected_plant")
    op.add_column(
        table_name, sa.Column("pre", sa.String(), nullable=True, server_default="")
    )
    op.add_column(
        table_name,
        sa.Column("folder_name", sa.String(), nullable=True, server_default=""),
    )
    op.add_column(
        table_name,
        sa.Column("file_format", sa.String(), nullable=True, server_default=""),
    )
    op.add_column(
        table_name,
        sa.Column("affected_plant", sa.String(), nullable=True, server_default=""),
    )


def downgrade() -> None:
    op.drop_column(table_name, "pre")
    op.drop_column(table_name, "folder_name")
    op.drop_column(table_name, "file_format")
    op.drop_column(table_name, "affected_plant")
