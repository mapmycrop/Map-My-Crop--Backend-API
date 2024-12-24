"""add_social_login_columns_to_users_table

Revision ID: 35ac2cb3305f
Revises: faa687335e96
Create Date: 2023-02-13 05:28:59.564750

"""

from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa

from variables import SocialLoginProviderType


# revision identifiers, used by Alembic.
revision = "35ac2cb3305f"
down_revision = "faa687335e96"
branch_labels = None
depends_on = None
table_name = "users"


def upgrade() -> None:
    social_login_provider_type = postgresql.ENUM(SocialLoginProviderType, name="status")
    social_login_provider_type.create(op.get_bind(), checkfirst=True)
    op.add_column(table_name, sa.Column("provider_key", sa.String(), nullable=True))
    op.add_column(
        table_name,
        sa.Column(
            "provider_type",
            social_login_provider_type,
            server_default=SocialLoginProviderType.none.value,
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(table_name, "provider_key")
    op.drop_column(table_name, "provider_type")
