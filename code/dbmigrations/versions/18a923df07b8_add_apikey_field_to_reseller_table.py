"""add apikey field to reseller table

Revision ID: 18a923df07b8
Revises: b6c3cd85fe2a
Create Date: 2024-04-21 19:40:45.781854

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = "18a923df07b8"
down_revision = "b6c3cd85fe2a"
branch_labels = None
depends_on = None

table_name = "resellers"


def upgrade() -> None:
    op.add_column(table_name, sa.Column("apikey", sa.String, unique=True))

    connection = op.get_bind()

    reseller_ids = connection.execute(text(f"SELECT id FROM {table_name}")).fetchall()

    for reseller_id in reseller_ids:
        apikey = str(uuid4())
        connection.execute(
            text(f"UPDATE {table_name} SET apikey = :apikey WHERE id = :id"),
            apikey=apikey,
            id=reseller_id[0],
        )


def downgrade() -> None:
    op.drop_column(table_name, "apikey")
