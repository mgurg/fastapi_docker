"""add_items_table

Revision ID: 38e5957fa66f
Revises: b2e42964ad3f
Create Date: 2023-04-26 17:54:59.069712

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = "38e5957fa66f"
down_revision = "b2e42964ad3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=512), unique=False, nullable=False),
        sa.Column("symbol", sa.VARCHAR(length=64), unique=False, nullable=True),
        sa.Column("summary", sa.VARCHAR(length=1024), unique=False, nullable=False),
        sa.Column("text", postgresql.TEXT, autoincrement=False, nullable=True),
        sa.Column("text_json", postgresql.JSONB, autoincrement=False, nullable=True),
        sa.Column("qr_code_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("public_access", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        # sa.ForeignKeyConstraint(["qr_code_id"], ["qr_codes.id"], name="qr_code_fk"),
        sa.PrimaryKeyConstraint("id", name="items_pkey"),
        schema=None,
    )
    op.create_table(
        "files_items_link",
        sa.Column("item_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("file_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], name="files_items_link_fk"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name="files_items_link_fk_1"),
        sa.PrimaryKeyConstraint("item_id", "file_id", name="files_items_link_pkey"),
        schema=None,
    )

    op.create_table(
        "users_items_link",
        sa.Column("item_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="users_items_link_fk"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name="users_items_link_fk_1"),
        sa.PrimaryKeyConstraint("item_id", "user_id", name="users_items_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("files_items_link_fk", "files_items_link")
    op.drop_constraint("files_items_link_fk_1", "files_items_link")
    op.drop_constraint("files_items_link_pkey", "files_items_link")

    op.drop_constraint("users_items_link_fk", "users_items_link")
    op.drop_constraint("users_items_link_fk_1", "users_items_link")
    op.drop_constraint("users_items_link_pkey", "users_items_link")

    op.drop_table("items", schema=None)
    op.drop_table("files_items_link", schema=None)
    op.drop_table("users_items_link", schema=None)
