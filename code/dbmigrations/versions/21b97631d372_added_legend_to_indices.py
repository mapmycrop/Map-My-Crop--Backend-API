"""added legend to indices

Revision ID: 21b97631d372
Revises: ab81afcb06d5
Create Date: 2023-01-20 19:38:15.384024

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "21b97631d372"
down_revision = "ab81afcb06d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('spatial_ref_sys')
    # op.create_index(op.f("ix_contacts_id"), "contacts", ["id"], unique=False)
    # op.alter_column("farm", "country", existing_type=sa.VARCHAR(), nullable=False)
    # op.alter_column("farm", "state", existing_type=sa.VARCHAR(), nullable=False)
    # op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)
    op.add_column("indice", sa.Column("legend", sa.JSON(), nullable=True))
    # op.alter_column(
    #     "predict_disease", "crop_id", existing_type=sa.VARCHAR(), nullable=True
    # )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.alter_column(
    #     "predict_disease", "crop_id", existing_type=sa.VARCHAR(), nullable=False
    # )
    op.drop_column("indice", "legend")
    # op.drop_index(op.f("ix_feedback_id"), table_name="feedback")
    # op.alter_column("farm", "state", existing_type=sa.VARCHAR(), nullable=True)
    # op.alter_column("farm", "country", existing_type=sa.VARCHAR(), nullable=True)
    # op.drop_index(op.f("ix_contacts_id"), table_name="contacts")
    # op.create_table('spatial_ref_sys',
    # sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    # sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    # sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    # sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.CheckConstraint('(srid > 0) AND (srid <= 998999)', name='spatial_ref_sys_srid_check'),
    # sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    # )
    # ### end Alembic commands ###
