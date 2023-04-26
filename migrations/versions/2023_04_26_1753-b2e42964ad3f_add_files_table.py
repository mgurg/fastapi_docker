"""add_files_table

Revision ID: b2e42964ad3f
Revises: a1b0cf6b2fbb
Create Date: 2023-04-26 17:53:19.260665

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table


# revision identifiers, used by Alembic.
revision = "b2e42964ad3f"
down_revision = "a1b0cf6b2fbb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("owner_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("file_name", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("file_description", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("extension", sa.VARCHAR(length=8), autoincrement=False, nullable=True),
        sa.Column("mimetype", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("size", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="files_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table("files", schema=None)
