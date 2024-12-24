"""update_contact_table

Revision ID: e579632e383a
Revises: 765003d8cfa1
Create Date: 2023-09-01 02:59:42.348706

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "e579632e383a"
down_revision = "765003d8cfa1"
branch_labels = None
depends_on = None

table_name = "contacts"


def upgrade() -> None:
    op.drop_column(table_name, "name")
    op.drop_column(table_name, "request_type")

    source = ("Web", "Mobile")
    contact_source = sa.Enum(*source, name="contact_source")
    contact_source.create(op.get_bind(), checkfirst=False)
    op.add_column(
        table_name,
        sa.Column(
            "source",
            sa.Enum("Web", "Mobile", name="contact_source"),
            nullable=True,
            server_default="Web",
        ),
    )

    op.create_foreign_key("fk_contact_user", "contacts", "users", ["user_id"], ["id"])


def downgrade() -> None:
    op.add_column(table_name, sa.Column("name", sa.String(), nullable=True))
    op.add_column(table_name, sa.Column("request_type", sa.String(), nullable=True))
    op.drop_column(table_name, "source")
    op.drop_constraint("fk_contact_user", table_name)
