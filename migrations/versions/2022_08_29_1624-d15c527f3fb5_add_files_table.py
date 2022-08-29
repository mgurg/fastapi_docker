"""Add Files Table

Revision ID: d15c527f3fb5
Revises: 338496320c4d
Create Date: 2022-08-29 16:24:18.140607

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "d15c527f3fb5"
down_revision = "338496320c4d"
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
