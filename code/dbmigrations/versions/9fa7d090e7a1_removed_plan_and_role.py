"""removed plan and role

Revision ID: 9fa7d090e7a1
Revises: 2051c58020fd
Create Date: 2022-11-22 23:25:25.714260

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9fa7d090e7a1"
down_revision = "2051c58020fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('spatial_ref_sys')
    op.drop_column("users", "role")
    op.drop_column("users", "plan_type")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("plan_type", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "users", sa.Column("role", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
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
