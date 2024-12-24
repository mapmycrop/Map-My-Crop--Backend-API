"""update_note_type_column

Revision ID: 9acd7937db4c
Revises: 8a86006ed4d1
Create Date: 2023-05-10 11:33:21.932877

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9acd7937db4c"
down_revision = "8a86006ed4d1"
branch_labels = None
depends_on = None

old_options = ("Disease", "Pests", "Water logging", "Weeds", "Lodging", "Others")
new_options = sorted(
    old_options
    + (
        "Ground Visit",
        "Soil Moisture Readings",
        "Soil Temperature Readings",
        "Soil Sample Collection",
        "Physical Infections Inspections",
        "Fungal Attack",
        "Irrigation Issues",
    )
)

old_type = sa.Enum(*old_options, name="note_types")
new_type = sa.Enum(*new_options, name="note_types")
tmp_type = sa.Enum(*old_options, name="_note_types")


def upgrade():
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE scoutings ALTER COLUMN note_type TYPE _note_types"
        " USING note_type::text::_note_types"
    )

    old_type.drop(op.get_bind(), checkfirst=False)

    new_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE scoutings ALTER COLUMN note_type TYPE note_types"
        " USING note_type::text::note_types"
    )

    tmp_type.drop(op.get_bind(), checkfirst=False)


def downgrade() -> None:
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE scoutings ALTER COLUMN note_type TYPE _note_types"
        " USING note_type::text::_note_types"
    )

    new_type.drop(op.get_bind(), checkfirst=False)

    old_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE scoutings ALTER COLUMN note_type TYPE note_types"
        " USING note_type::text::note_types"
    )

    tmp_type.drop(op.get_bind(), checkfirst=False)
