"""Add Ideas Table

Revision ID: 7d10cd2a559b
Revises: d15c527f3fb5
Create Date: 2022-08-29 16:26:24.401371

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "7d10cd2a559b"
down_revision = "d15c527f3fb5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ideas",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("color", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("title", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("upvotes", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("downvotes", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("status", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="ideas_pkey"),
        schema=None,
    )

    op.create_table(
        "ideas_files_link",
        sa.Column("idea_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("file_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], name="ideas_files_link_fk"),
        sa.ForeignKeyConstraint(["idea_id"], ["ideas.id"], name="ideas_files_link_fk_1"),
        sa.PrimaryKeyConstraint("idea_id", "file_id", name="ideas_files_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("ideas_files_link_fk", "ideas_files_link")
    op.drop_constraint("ideas_files_link_fk_1", "ideas_files_link")
    op.drop_constraint("ideas_files_link_pkey", "ideas_files_link")
    op.drop_table("ideas", schema=None)
    op.drop_table("ideas_files_link", schema=None)
