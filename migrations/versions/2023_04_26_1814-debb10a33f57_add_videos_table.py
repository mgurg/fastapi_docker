"""add_videos_table

Revision ID: debb10a33f57
Revises: 3e3981bb512d
Create Date: 2023-04-26 18:14:19.648514

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "debb10a33f57"
down_revision = "3e3981bb512d"
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
