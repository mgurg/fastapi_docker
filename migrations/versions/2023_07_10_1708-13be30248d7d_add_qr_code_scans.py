"""add QR Code Scans

Revision ID: 13be30248d7d
Revises: cec65e1bd0de
Create Date: 2023-07-10 17:08:58.348097

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "13be30248d7d"
down_revision = "cec65e1bd0de"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "qr_code_scans",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("qr_code_id", sa.VARCHAR(length=32), autoincrement=False, nullable=True),
        sa.Column("resource", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("resource_uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("ua", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("browser", sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column("system", sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column("device", sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column("ip", sa.VARCHAR(length=64), autoincrement=False, nullable=True),
        sa.Column("lang", sa.VARCHAR(length=8), autoincrement=False, nullable=True),
        sa.Column("country", sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column("city", sa.VARCHAR(length=128), autoincrement=False, nullable=True),
        sa.Column("lat", sa.DECIMAL(10, 8), autoincrement=False, nullable=True),
        sa.Column("lon", sa.DECIMAL(10, 8), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="qr_code_scans_pkey"),
        schema=None,
    )


def downgrade() -> None:
    pass
