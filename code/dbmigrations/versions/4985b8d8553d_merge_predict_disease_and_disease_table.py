"""Merge predict_disease and disease table

Revision ID: 4985b8d8553d
Revises: 9470c0081a8b
Create Date: 2023-05-22 09:36:23.652116

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4985b8d8553d"
down_revision = "9470c0081a8b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("predict_disease")
    op.drop_column("disease", "affected_plant")
    op.add_column("disease", sa.Column("class_name", sa.String(), nullable=True))
    op.add_column("disease", sa.Column("crop_id", sa.String(), nullable=True))
    op.create_unique_constraint("uq_disease_class_name", "disease", ["class_name"])
    op.create_foreign_key(
        "fk_disease_crop_id",
        "disease",
        "crop",
        ["crop_id"],
        ["id"],
    )
    op.alter_column("disease", "causes", nullable=True, server_default=None)
    op.alter_column("disease", "organic_control", nullable=True)
    op.alter_column("disease", "chemical_control", nullable=True)
    op.alter_column("disease", "preventive_measures", nullable=True)
    op.alter_column("disease", "pre", nullable=True, server_default=None)
    op.alter_column("disease", "folder_name", nullable=True, server_default=None)
    op.alter_column("disease", "file_format", nullable=True, server_default=None)


def downgrade() -> None:
    op.create_table(
        "predict_disease",
        (
            sa.Column("class_name", sa.String(length=255), nullable=False),
            sa.Column("disease", sa.String(length=255), nullable=False),
            sa.Column("crop_id", sa.String(length=255), nullable=False),
            sa.Column("symptoms", sa.String(length=255), nullable=True),
            sa.Column("causes", sa.String(length=255), nullable=True),
            sa.Column("organic_control", sa.String(length=255), nullable=True),
            sa.Column("chemical_control", sa.String(length=255), nullable=True),
            sa.Column("preventive_measures", sa.String(length=255), nullable=True),
            sa.PrimaryKeyConstraint("class_name"),
            sa.ForeignKeyConstraint(["crop_id"], ["crop.id"]),
        ),
    )
    op.add_column(
        "disease",
        sa.Column("affected_plant", sa.String(), nullable=False, server_default=""),
    )
    op.drop_constraint("uq_disease_class_name", "disease")
    op.drop_constraint("fk_disease_crop_id", "disease")
    op.drop_column("disease", "class_name")
    op.drop_column("disease", "crop_id")
    op.alter_column("disease", "causes", nullable=True)
    op.alter_column("disease", "organic_control", nullable=True)
    op.alter_column("disease", "chemical_control", nullable=True)
    op.alter_column("disease", "preventive_measures", nullable=True)
    op.alter_column("disease", "pre", nullable=True)
    op.alter_column("disease", "folder_name", nullable=True)
    op.alter_column("disease", "file_format", nullable=True)
