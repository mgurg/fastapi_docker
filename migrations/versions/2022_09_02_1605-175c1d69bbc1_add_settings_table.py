"""add settings table

Revision ID: 175c1d69bbc1
Revises: 7d10cd2a559b
Create Date: 2022-09-02 16:05:35.414367

"""
from enum import unique

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "175c1d69bbc1"
down_revision = "7d10cd2a559b"
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

    # StringValue
    # IntValue
    # DateValue
    # DecimalValue


def downgrade() -> None:
    op.drop_table("settings", schema=None)
