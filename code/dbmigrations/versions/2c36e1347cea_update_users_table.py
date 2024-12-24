"""update_users_table

Revision ID: 2c36e1347cea
Revises: 82db5c398dc5
Create Date: 2023-10-31 22:18:52.859050

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from variables import SocialLoginProviderType


# revision identifiers, used by Alembic.
revision = "2c36e1347cea"
down_revision = "82db5c398dc5"
branch_labels = None
depends_on = None
table_name = "users"


def upgrade() -> None:
    op.alter_column(
        table_name="users",
        column_name="ph",
        nullable=True,
        existing_type=sa.BigInteger(),
        type_=sa.String(),
    )
    op.drop_column("users", "provider_key")
    op.drop_column("users", "provider_type")
    op.drop_column("users", "adhaar")


def downgrade() -> None:
    op.alter_column(
        table_name="users",
        column_name="ph",
        nullable=True,
        existing_type=sa.String(),
        type_=sa.BigInteger(),
    )
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
    op.add_column("users", sa.Column("adhaar", sa.String(), nullable=True))
    op.create_unique_constraint(None, "users", ["adhaar"])
