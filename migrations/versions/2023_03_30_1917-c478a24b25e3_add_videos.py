"""Add videos

Revision ID: c478a24b25e3
Revises: cd7a995ecaf6
Create Date: 2023-03-30 19:17:44.735097

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = 'c478a24b25e3'
down_revision = 'cd7a995ecaf6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "videos",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("video_id", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("video_json", postgresql.JSONB, autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("duration", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("size", sa.INTEGER(), autoincrement=False, nullable=False),
        # sa.Column("color", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        # sa.Column("icon", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        # sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=False),
        # sa.Column("is_hidden", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="videos_pkey"),
        sa.UniqueConstraint("name", "deleted_at", name="video_name_key"),
        schema=None,
    )

    op.create_table(
        "videos_guides_link",
        sa.Column("guide_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("video_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], name="videos_guides_link_fk"),
        sa.ForeignKeyConstraint(["guide_id"], ["guides.id"], name="videos_guides_link_fk_1"),
        sa.PrimaryKeyConstraint("guide_id", "video_id", name="videos_guides_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("videos_guides_link_fk", "videos_guides_link")
    op.drop_constraint("videos_guides_link_fk_1", "videos_guides_link")
    op.drop_constraint("videos_guides_link_pkey", "videos_guides_link")

    op.drop_table("videos", schema=None)
    op.drop_table("videos_guides_link", schema=None)
