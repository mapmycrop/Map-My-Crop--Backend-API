"""update_statistic_table

Revision ID: d60d9a01f973
Revises: 3a2066bc69a7
Create Date: 2023-06-15 02:34:43.551871

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d60d9a01f973"
down_revision = "3a2066bc69a7"
branch_labels = None
depends_on = None
table_name = "statistic"


def upgrade() -> None:
    op.alter_column(
        table_name, column_name="paying_farmers", new_column_name="paid_farms"
    )
    op.alter_column(
        table_name, column_name="non_paying_farmers", new_column_name="non_paid_farms"
    )
    op.drop_column(table_name, "countrywise_farmers")


def downgrade() -> None:
    op.alter_column(
        table_name, column_name="paid_farms", new_column_name="paying_farmers"
    )
    op.alter_column(
        table_name, column_name="non_paid_farms", new_column_name="non_paying_farmers"
    )
    op.add_column(
        table_name, sa.Column("countrywise_farmers", sa.Integer(), nullable=False)
    )
