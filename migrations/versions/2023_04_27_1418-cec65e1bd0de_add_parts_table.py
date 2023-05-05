"""Add parts table

Revision ID: cec65e1bd0de
Revises: debb10a33f57
Create Date: 2023-04-27 14:18:03.643717

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "cec65e1bd0de"
down_revision = "debb10a33f57"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "parts_used",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True, index=True),
        sa.Column("item_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("issue_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("author_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("name", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=512), autoincrement=False, nullable=True),
        sa.Column("price", sa.DECIMAL(10, 2), autoincrement=False, nullable=True),
        sa.Column("quantity", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("unit", sa.VARCHAR(length=32), autoincrement=False, nullable=True),
        sa.Column("value", sa.DECIMAL(10, 2), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("deleted_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="parts_used_pkey"),
        sa.UniqueConstraint("name", "deleted_at", name="part_used_name_key"),
        schema=None,
    )

    # op.create_table(
    #     "parts_used_issues_link",
    #     sa.Column("issue_id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
    #     sa.Column("part_used_id", sa.INTEGER(), autoincrement=False, nullable=False),
    #     # sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=True),
    #     sa.ForeignKeyConstraint(["part_used_id"], ["parts_used.id"], name="parts_used_issues_link_fk"),
    #     sa.ForeignKeyConstraint(["issue_id"], ["issues.id"], name="parts_used_issues_link_fk_1"),
    #     sa.PrimaryKeyConstraint("issue_id", "part_used_id", name="parts_used_issues_link_pkey"),
    #     schema=None,
    # )


def downgrade() -> None:
    # op.drop_constraint("parts_used_issues_link_fk", "parts_used_issues_link")
    # op.drop_constraint("parts_used_issues_link_fk_1", "parts_used_issues_link")
    # op.drop_constraint("parts_used_issues_link_pkey", "parts_used_issues_link")

    op.drop_table("parts_used", schema=None)
    # op.drop_table("parts_used_issues_link", schema=None)
