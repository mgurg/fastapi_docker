"""Add Tables Users, Roles, Permissions

Revision ID: e3aad4a7daff
Revises: 43de4e824162
Create Date: 2022-07-20 14:19:33.700542

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e3aad4a7daff"
down_revision = "43de4e824162"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("is_custom", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("is_visible", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("role_name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("role_title", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("role_description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="roles_pkey"),
        schema=None,
    )
    op.create_table(
        "users",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("email", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("password", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("tos", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("first_name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("last_name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("user_role_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("auth_token", sa.VARCHAR(length=128), autoincrement=False, nullable=True, unique=True),
        sa.Column("auth_token_valid_to", sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("is_verified", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("service_token", sa.VARCHAR(length=100), autoincrement=False, nullable=True, unique=True),
        sa.Column("service_token_valid_to", sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("tz", sa.VARCHAR(length=64), autoincrement=False, nullable=False),
        sa.Column("lang", sa.VARCHAR(length=8), autoincrement=False, nullable=False),
        sa.Column("tenant_id", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["user_role_id"], ["roles.id"], name="role_fk"),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
        sa.UniqueConstraint("email", name="users_email_key"),
        schema=None,
    )
    op.create_table(
        "permissions",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("title", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="permissions_pkey"),
        sa.UniqueConstraint("uuid", name="permissions_uuid_key"),
        schema=None,
    )

    op.create_table(
        "roles_permissions_link",
        sa.Column("role_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("permission_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], name="roles_permissions_link_fk"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name="roles_permissions_link_fk_1"),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name="roles_permissions_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("roles_permissions_link_fk", "roles_permissions_link")
    op.drop_constraint("roles_permissions_link_fk_1", "roles_permissions_link")
    op.drop_constraint("roles_permissions_link_pkey", "roles_permissions_link")
    op.drop_table("permissions", schema=None)
    op.drop_table("users", schema=None)
    op.drop_table("roles", schema=None)
    op.drop_table("roles_permissions_link", schema=None)
