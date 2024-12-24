"""create_role_table_and_relationship

Revision ID: 301d2e773c35
Revises: a4752cff0d2e
Create Date: 2023-04-18 08:27:36.613242

"""

from alembic import op
from sqlalchemy import orm
import sqlalchemy as sa

from models import User, Company, Role


# revision identifiers, used by Alembic.
revision = "301d2e773c35"
down_revision = "01a5594b8b1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    Role.__table__.create(bind)

    roles = [
        {"id": 1, "name": "Farmer", "description": "User who can add farms"},
        {"id": 2, "name": "Company", "description": "Admin of Company"},
        {"id": 3, "name": "Super Admin", "description": "Role of super admin for MMC"},
        {"id": 4, "name": "Agronomists", "description": "Scientists of MMC"},
    ]

    session.add_all(
        [
            Role(id=role["id"], name=role["name"], description=role["description"])
            for role in roles
        ]
    )
    session.commit()

    op.add_column("companies", sa.Column("role", sa.Integer(), default=2))
    op.create_foreign_key("fk_company_role", "companies", "roles", ["role"], ["id"])

    bind.execute(f"update companies set role = 2")

    op.add_column("users", sa.Column("role_id", sa.Integer()))

    for user in session.query(User.role, User.id):
        role = 1

        if user.role == "company":
            role = 2

        if user.role == "superadmin":
            role = 3

        if user.role == "agronomist":
            role = 4

        bind.execute(f"update users set role_id = {role} where id = {user.id}")

    op.drop_column("users", "role")
    op.alter_column(
        table_name="users",
        column_name="role_id",
        existing_type=sa.Integer(),
        new_column_name="role",
    )
    op.create_foreign_key("fk_user_role", "users", "roles", ["role"], ["id"])


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.drop_constraint("companies", "fk_company_role")
    op.drop_column("companies", "role")

    op.drop_constraint("users", "fk_user_role")
    op.alter_column(
        table_name="users",
        column_name="role",
        existing_type=sa.Integer(),
        type_=sa.String(),
    )

    for user in session.query(User):
        user_role = "Farmer"

        role = session.query(Role).filter(Role.id == int(user.role)).first()

        if role:
            user_role = role.name

        user.role = user_role

    session.commit()

    op.drop_table("roles")
