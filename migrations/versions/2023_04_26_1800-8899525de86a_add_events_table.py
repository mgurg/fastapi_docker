"""add_events_table

Revision ID: 8899525de86a
Revises: 249aba91b072
Create Date: 2023-04-26 18:00:43.460927

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8899525de86a"
down_revision = "249aba91b072"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=False, index=True),
        sa.Column("action", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("action_from", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("action_to", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("internal_value", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("resource", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("resource_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("resource_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=True),
        # sa.Column("author_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        # sa.Column("author_name", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="event_user_link_fk"),
        sa.PrimaryKeyConstraint("id", name="events_pkey"),
        schema=None,
    )

    op.create_table(
        "events_summary",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=False),
        sa.Column("resource", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("resource_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("action", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("date_from", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("date_to", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("duration", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("internal_value", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="events_summary_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("event_user_link_fk", "events")
    op.drop_table("events", schema=None)
    op.drop_table("events_summary", schema=None)
