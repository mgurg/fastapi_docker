"""add_issues_table

Revision ID: 249aba91b072
Revises: 7283939d25ad
Create Date: 2023-04-26 17:59:32.188568

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "249aba91b072"
down_revision = "7283939d25ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "issues",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=False, index=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("author_name", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("item_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("symbol", sa.VARCHAR(length=32), unique=True, nullable=False),
        sa.Column("summary", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("text", sa.TEXT, autoincrement=False, nullable=True),
        sa.Column("text_json", postgresql.JSONB, autoincrement=False, nullable=True),
        sa.Column("color", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("priority", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("status", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name="issue_item_link_fk"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="issue_user_link_fk_1"),
        sa.PrimaryKeyConstraint("id", name="issues_pkey"),
        schema=None,
    )

    op.create_table(
        "files_issues_link",
        sa.Column("issue_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("file_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], name="files_issues_link_fk"),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], name="files_issues_link_fk_1"),
        sa.PrimaryKeyConstraint("issue_id", "file_id", name="files_issues_link_pkey"),
        schema=None,
    )

    op.create_table(
        "users_issues_link",
        sa.Column("issue_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="users_issues_link_fk"),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], name="users_issues_link_fk_1"),
        sa.PrimaryKeyConstraint("issue_id", "user_id", name="users_issues_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("issue_item_link_fk", "issues")
    op.drop_constraint("issue_user_link_fk_1", "issues")

    op.drop_constraint("users_issues_link_fk", "users_issues_link")
    op.drop_constraint("users_issues_link_fk_1", "users_issues_link")
    op.drop_constraint("users_issues_link_pkey", "users_issues_link")

    op.drop_constraint("files_issues_link_fk", "files_issues_link")
    op.drop_constraint("files_issues_link_fk_1", "files_issues_link")
    op.drop_constraint("files_issues_link_pkey", "files_issues_link")

    op.drop_table("issues", schema=None)

    op.drop_table("files_issues_link", schema=None)
    op.drop_table("user_issues_link", schema=None)
