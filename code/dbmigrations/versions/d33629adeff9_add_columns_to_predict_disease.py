"""add columns to predict disease

Revision ID: d33629adeff9
Revises: 36bfcedf6c36
Create Date: 2022-12-27 12:42:35.368731

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d33629adeff9"
down_revision = "36bfcedf6c36"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("predict_disease", sa.Column("symptoms", sa.String()))
    op.add_column("predict_disease", sa.Column("causes", sa.String()))
    op.add_column("predict_disease", sa.Column("organic_control", sa.String()))
    op.add_column("predict_disease", sa.Column("chemical_control", sa.String()))
    op.add_column("predict_disease", sa.Column("preventive_measures", sa.String()))


def downgrade() -> None:
    op.drop_column("predict_disease", "symptoms")
    op.drop_column("predict_disease", "causes")
    op.drop_column("predict_disease", "organic_control")
    op.drop_column("predict_disease", "chemical_control")
    op.drop_column("predict_disease", "preventive_measures")
