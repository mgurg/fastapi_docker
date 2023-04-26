"""add_qr_code_table

Revision ID: 40bde431a56f
Revises: 38e5957fa66f
Create Date: 2023-04-26 17:55:47.920796

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "40bde431a56f"
down_revision = "38e5957fa66f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "qr_codes",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("resource", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("resource_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("qr_code_id", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("qr_code_full_id", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("public_access", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("ecc", sa.CHAR(length=1), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="qr_codes_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table("qr_codes", schema=None)
