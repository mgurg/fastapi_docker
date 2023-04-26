"""add_tags_table

Revision ID: 3e3981bb512d
Revises: 8899525de86a
Create Date: 2023-04-26 18:01:25.632291

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "3e3981bb512d"
down_revision = "8899525de86a"
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
        sa.UniqueConstraint("name", "deleted_at", name="tag_name_key"),
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
