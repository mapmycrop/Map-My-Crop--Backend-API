"""update scouting table

Revision ID: a0002ae28ae8
Revises: d673ed1afc40
Create Date: 2024-04-15 22:15:01.054370

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a0002ae28ae8"
down_revision = "d673ed1afc40"
branch_labels = None
depends_on = None


table_name = "scoutings"


def upgrade():
    op.add_column(
        table_name,
        sa.Column("title", sa.String(), nullable=False, server_default="This is title"),
    )
    op.add_column(
        table_name,
        sa.Column(
            "due_date", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
    )
    op.add_column(
        table_name,
        sa.Column(
            "scouting_date", sa.DateTime(), nullable=True, server_default=sa.func.now()
        ),
    )
    op.add_column(
        table_name, sa.Column("attachments", sa.ARRAY(sa.String), nullable=True)
    )

    connection = op.get_bind()
    results = connection.execute("SELECT id, attachment FROM " + table_name)

    metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload=True, autoload_with=connection)

    for row in results:
        if row.attachment:
            attachment_list = row.attachment.split(",")

            connection.execute(
                table.update()
                .where(table.c.id == row.id)
                .values(attachments=attachment_list)
            )

    op.drop_column(table_name, "attachment")


def downgrade():
    op.add_column(table_name, sa.Column("attachment", sa.String(), nullable=True))

    connection = op.get_bind()
    results = connection.execute("SELECT id, attachments FROM " + table_name)

    metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload=True, autoload_with=connection)

    for row in results:
        attachment_string = ",".join(row.attachments)

        connection.execute(
            table.update()
            .where(table.c.id == row.id)
            .values(attachment=attachment_string)
        )

    op.drop_column(table_name, "attachments")
    op.drop_column(table_name, "title")
    op.drop_column(table_name, "due_date")
    op.drop_column(table_name, "scouting_date")
