"""Add Events Tables

Revision ID: 80d733751484
Revises: 9eaef88ed3fd
Create Date: 2022-12-28 12:30:47.553362

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "80d733751484"
down_revision = "9eaef88ed3fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("resource", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("resource_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("resource_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("action", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("author_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("author_name", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("value", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="events_pkey"),
        schema=None,
    )

    op.create_table(
        "events_summary",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("resource", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("resource_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("issue_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("action", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("date_from", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("date_to", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("duration", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="events_summary_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table("events", schema=None)
    op.drop_table("events_summary", schema=None)
