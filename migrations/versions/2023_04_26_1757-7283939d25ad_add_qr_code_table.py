"""add_guides_table

Revision ID: 7283939d25ad
Revises: 40bde431a56f
Create Date: 2023-04-26 17:57:32.574715

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7283939d25ad"
down_revision = "40bde431a56f"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "qr_codes",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=False, index=True),
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

    op.create_foreign_key("qr_code_items_fk", "items", "qr_codes", ["qr_code_id"], ["id"])
    op.create_foreign_key("qr_code_guides_fk", "guides", "qr_codes", ["qr_code_id"], ["id"])


def downgrade() -> None:
    op.drop_table("qr_codes", schema=None)