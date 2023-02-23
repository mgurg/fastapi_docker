"""Add Tags

Revision ID: cd7a995ecaf6
Revises: 80d733751484
Create Date: 2023-01-31 15:55:59.929491

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "cd7a995ecaf6"
down_revision = "80d733751484"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("color", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("icon", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("is_hidden", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="tags_pkey"),
        schema=None,
    )

    op.create_table(
        "tags_issues_link",
        sa.Column("issue_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("tag_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name="tags_issues_link_fk"),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], name="tags_issues_link_fk_1"),
        sa.PrimaryKeyConstraint("issue_id", "tag_id", name="tags_issues_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("tags_issues_link_fk", "tags_issues_link")
    op.drop_constraint("tags_issues_link_fk_1", "tags_issues_link")
    op.drop_constraint("tags_issues_link_pkey", "tags_issues_link")

    op.drop_table("tags", schema=None)
    op.drop_table("tags_issues_link", schema=None)
