"""add_qr_code_table

Revision ID: 40bde431a56f
Revises: 38e5957fa66f
Create Date: 2023-04-26 17:55:47.920796

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "40bde431a56f"
down_revision = "38e5957fa66f"
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "guides",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=False, index=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=512), unique=False, autoincrement=False, nullable=False),
        sa.Column("text", sa.TEXT, autoincrement=False, nullable=True),
        sa.Column("text_json", postgresql.JSONB, autoincrement=False, nullable=True),
        sa.Column("qr_code_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("type", sa.VARCHAR(length=32), unique=False, autoincrement=False, nullable=True),
        sa.Column("is_public", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="guide_user_link_fk"),
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

    op.create_table(
        "items_guides_link",
        sa.Column("guide_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("item_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name="items_guides_link_fk"),
        sa.ForeignKeyConstraint(["guide_id"], ["guides.id"], name="items_guides_link_fk_1"),
        sa.PrimaryKeyConstraint("guide_id", "item_id", name="items_guides_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("guide_user_link_fk", "guides")

    op.drop_constraint("files_guides_link_fk", "files_guides_link")
    op.drop_constraint("files_guides_link_fk_1", "files_guides_link")
    op.drop_constraint("files_guides_link_pkey", "files_guides_link")

    op.drop_constraint("items_guides_link_fk", "items_guides_link")
    op.drop_constraint("items_guides_link_fk_1", "items_guides_link")
    op.drop_constraint("items_guides_link_pkey", "items_guides_link")
    op.drop_table("items_guides_link", schema=None)

    op.drop_table("guides", schema=None)
    op.drop_table("files_guides_link", schema=None)


