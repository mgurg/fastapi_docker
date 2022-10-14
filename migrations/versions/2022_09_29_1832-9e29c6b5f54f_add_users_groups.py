"""Add Users Groups

Revision ID: 9e29c6b5f54f
Revises: 175c1d69bbc1
Create Date: 2022-09-29 18:32:45.219848

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "9e29c6b5f54f"
down_revision = "175c1d69bbc1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users_groups",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=256), unique=True, autoincrement=False, nullable=False),
        sa.Column("description", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("symbol", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("supervisor_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="users_groups_pkey"),
        schema=None,
    )

    op.create_table(
        "users_groups_link",
        sa.Column("user_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("user_group_id", sa.INTEGER(), autoincrement=False, nullable=False),
        # sa.Column("user_is_supervisor", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["user_group_id"], ["users_groups.id"], name="users_groups_link_fk"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="users_groups_link_fk_1"),
        sa.PrimaryKeyConstraint("user_id", "user_group_id", name="users_groups_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("users_groups_link_fk", "users_groups_link")
    op.drop_constraint("users_groups_link_fk_1", "users_groups_link")
    op.drop_constraint("users_groups_link_pkey", "users_groups_link")
    op.drop_table("users_groups", schema=None)
    op.drop_table("users_groups_link", schema=None)
