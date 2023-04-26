"""add_settings_table

Revision ID: a1b0cf6b2fbb
Revises: 055684700394
Create Date: 2023-04-26 17:52:02.820335

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "a1b0cf6b2fbb"
down_revision = "055684700394"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "settings",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(length=256), unique=True, autoincrement=False, nullable=True),
        sa.Column("value", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("value_type", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("prev_value", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("descripton", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("updated_by", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="settings_pkey"),
        schema=None,
    )

    op.create_table(
        "settings_users",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=256), unique=True, autoincrement=False, nullable=True),
        sa.Column("value", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("value_type", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("prev_value", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="settings_users_pkey"),
        schema=None,
    )

    op.create_table(
        "settings_notifications",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("user_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("sms_notification_level", sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column("email_notification_level", sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="user_notification_fk"),
        sa.PrimaryKeyConstraint("id", name="settings_notifications_pkey"),
        schema=None,
    )

    # StringValue
    # IntValue
    # DateValue
    # DecimalValue


def downgrade() -> None:
    op.drop_table("settings", schema=None)
    op.drop_table("settings_user", schema=None)
    op.drop_table("settings_notifications", schema=None)
