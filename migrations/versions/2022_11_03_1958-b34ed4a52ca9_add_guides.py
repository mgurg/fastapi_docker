"""Add Guides

Revision ID: b34ed4a52ca9
Revises: b6ec5354ff82
Create Date: 2022-11-03 19:58:16.487750

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "b34ed4a52ca9"
down_revision = "b6ec5354ff82"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "guides",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("resource", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("resource_id", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=256), unique=False, autoincrement=False, nullable=False),
        sa.Column("is_starred", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("text", sa.TEXT, autoincrement=False, nullable=True),
        sa.Column("text_jsonb", postgresql.JSONB, autoincrement=False, nullable=True),
        sa.Column("video_id", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("video_jsonb", postgresql.JSONB, autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="guides_pkey"),
        schema=None,
    )

    op.create_table(
        "files_guides_link",
        sa.Column("guide_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("file_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], name="files_guides_link_fk"),
        sa.ForeignKeyConstraint(["guide_id"], ["guides.id"], name="files_guides_link_fk_1"),
        sa.PrimaryKeyConstraint("guide_id", "file_id", name="files_guides_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table("guides", schema=None)
