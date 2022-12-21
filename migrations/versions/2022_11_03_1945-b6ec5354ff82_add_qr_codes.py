"""Add QR codes

Revision ID: b6ec5354ff82
Revises: f0ae7b9d9467
Create Date: 2022-11-03 19:45:16.720097

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "b6ec5354ff82"
down_revision = "f0ae7b9d9467"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "qr_codes",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("resource", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("qr_code_id", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("qr_code_full_id", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("ecc", sa.CHAR(length=1), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="qr_codes_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table("qr_codes", schema=None)
