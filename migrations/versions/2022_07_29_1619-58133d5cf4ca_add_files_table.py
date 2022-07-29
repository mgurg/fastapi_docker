"""Add files table

Revision ID: 58133d5cf4ca
Revises: 9efdd94249a5
Create Date: 2022-07-29 16:19:35.212098

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "58133d5cf4ca"
down_revision = "9efdd94249a5"
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
        sa.PrimaryKeyConstraint("id", name="roles_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table("files", schema=None)
