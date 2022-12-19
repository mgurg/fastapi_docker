"""Add items

Revision ID: f0ae7b9d9467
Revises: 9e29c6b5f54f
Create Date: 2022-11-03 16:30:24.274618

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "f0ae7b9d9467"
down_revision = "9e29c6b5f54f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "items",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=256), unique=False, autoincrement=False, nullable=False),
        sa.Column("description", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("description_jsonb", postgresql.JSONB, autoincrement=False, nullable=True),
        sa.Column("qr_code_id", sa.INTEGER(), autoincrement=False, nullable=True),
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


def downgrade() -> None:
    op.drop_constraint("files_items_link_fk", "files_items_link")
    op.drop_constraint("files_items_link_fk_1", "files_items_link")
    op.drop_constraint("files_items_link_pkey", "files_items_link")
    op.drop_table("items", schema=None)
    op.drop_table("files_items_link", schema=None)
