"""Initial Tenant Tables

Revision ID: 43de4e824162
Revises: d6ba8c13303e
Create Date: 2022-07-18 16:18:40.239282

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "43de4e824162"
down_revision = "d6ba8c13303e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table("books", schema=None)
