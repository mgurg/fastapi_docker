"""Add items_guides_link

Revision ID: de539d00b411
Revises: b34ed4a52ca9
Create Date: 2022-12-01 14:36:42.350236

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "de539d00b411"
down_revision = "b34ed4a52ca9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "items_guides_link",
        sa.Column("guide_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("item_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], name="items_guides_link_fk"),
        sa.ForeignKeyConstraint(["guide_id"], ["guides.id"], name="items_guides_link_fk_1"),
        sa.PrimaryKeyConstraint("guide_id", "item_id", name="items_guides_link_pkey"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_constraint("items_guides_link_fk", "items_guides_link")
    op.drop_constraint("items_guides_link_fk_1", "items_guides_link")
    op.drop_constraint("items_guides_link_pkey", "items_guides_link")
    op.drop_table("items_guides_link", schema=None)
