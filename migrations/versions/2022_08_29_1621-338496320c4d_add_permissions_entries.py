"""Add Permissions Entries

Revision ID: 338496320c4d
Revises: 80726328353e
Create Date: 2022-08-29 16:21:50.746079

"""
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "338496320c4d"
down_revision = "80726328353e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    permissions = table(
        "permissions",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("title", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("group", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    )

    op.bulk_insert(
        permissions,
        [
        # USERS
            {
                "uuid": uuid4(),
                "name": "USER_VIEW",
                "title": "Show Users section in menu",
                "description": "User has acces to Users section",
                "group": "users"
            },
            {
                "uuid": uuid4(),
                "name": "USER_ADD",
                "title": "Adding users",
                "description": "User can create new user accounts",
                "group": "users"
            },
            {
                "uuid": uuid4(),
                "name": "USER_EDIT",
                "title": "Modifying users",
                "description": "User can edit other users accounts",
                "group": "users"
            },
                        {
                "uuid": uuid4(),
                "name": "USER_EDIT_SELF",
                "title": "Modifying ourself",
                "description": "User can edit his account",
                "group": "users"
            },
            {
                "uuid": uuid4(),
                "name": "USER_DELETE",
                "title": "Removing users",
                "description": "User can delete other users accounts",
                "group": "users"
            },
            {
                "uuid": uuid4(),
                "name": "USER_IMPORT",
                "title": "Importing users",
                "description": "User can import  users data from CSV file",
                "group": "users"
            },
            {
                "uuid": uuid4(),
                "name": "USER_EXPORT",
                "title": "Exporting users",
                "description": "User can export users data to CSV",
                "group": "users"
            },
# ISSUES
            {
                "uuid": uuid4(),
                "name": "ISSUE_VIEW",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_ADD",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_EDIT",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_DELETE",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_EXCLUDE",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_USER_ASSIGN",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_WORK_CONTROLS",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_SHOw_HISTORY",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_COMMENTS",
                "title": "",
                "description": "",
                "group": "issues"
            },
            {
                "uuid": uuid4(),
                "name": "ISSUE_REPLACED_PARTS",
                "title": "",
                "description": "",
                "group": "issues"
            },
# ITEMS
            {
                "uuid": uuid4(),
                "name": "ITEM_VIEW",
                "title": "",
                "description": "",
                "group": "items"
            },
            {
                "uuid": uuid4(),
                "name": "ITEM_ADD",
                "title": "",
                "description": "",
                "group": "items"
            },
            {
                "uuid": uuid4(),
                "name": "ITEM_EDIT",
                "title": "",
                "description": "",
                "group": "items"
            },
            {
                "uuid": uuid4(),
                "name": "ITEM_HIDE",
                "title": "",
                "description": "",
                "group": "items"
            },
            {
                "uuid": uuid4(),
                "name": "ITEM_SHOW_QR",
                "title": "",
                "description": "",
                "group": "items"
            },
            {
                "uuid": uuid4(),
                "name": "ITEM_SHOw_HISTORY",
                "title": "",
                "description": "",
                "group": "items"
            },
            {
                "uuid": uuid4(),
                "name": "ITEM_COMMENTS",
                "title": "",
                "description": "",
                "group": "items"
            },

# TAGS
            {
                "uuid": uuid4(),
                "name": "TAG_ADD",
                "title": "",
                "description": "",
                "group": "tags"
            },
            {
                "uuid": uuid4(),
                "name": "TAG_EDIT",
                "title": "",
                "description": "",
                "group": "tags"
            },
            {
                "uuid": uuid4(),
                "name": "TAG_HIDE",
                "title": "",
                "description": "",
                "group": "tags"
            },
            {
                "uuid": uuid4(),
                "name": "TAG_DELETE",
                "title": "",
                "description": "",
                "group": "tags"
            },
# SETTINGS 
            {
                "uuid": uuid4(),
                "name": "SETTINGS_IDEAS",
                "title": "Acces to Idea's Settings",
                "description": "User can change Idea related settings",
                "group": "settings"
            },
            {
                "uuid": uuid4(),
                "name": "SETTINGS_ROLES",
                "title": "Acces to Role's Settings",
                "description": "User can change Roles related settings",
                "group": "settings"
            },
            {
                "uuid": uuid4(),
                "name": "SETTINGS_GROUPS",
                "title": "Acces to Groups's Settings",
                "description": "User can change Groups related settings",
                "group": "settings"
            },
        ],
    )

    roles = table(
        "roles",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("is_custom", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("is_visible", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("role_name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("role_title", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("role_description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    )

    op.bulk_insert(
        roles,
        [
            {
                "uuid": uuid4(),
                "is_custom": False,
                "is_visible": True,
                "role_name": "ADMIN_MASTER",
                "role_title": "Main admin",
                "role_description": "Main admin role",
            },
            {
                "uuid": uuid4(),
                "is_custom": False,
                "is_visible": True,
                "role_name": "ADMIN",
                "role_title": "Admin",
                "role_description": "Admin role",
            },
        ],
    )

    roles_permissions_link = table(
        "roles_permissions_link",
        sa.Column("role_id", sa.ForeignKey("roles.id"), autoincrement=False, nullable=False, primary_key=True),
        sa.Column(
            "permission_id", sa.ForeignKey("permissions.id"), autoincrement=False, nullable=False, primary_key=True
        ),
    )

    op.bulk_insert(
        roles_permissions_link,
        [
            {
                "role_id": 1,
                "permission_id": 1,
            },
            {
                "role_id": 1,
                "permission_id": 2,
            },
            {
                "role_id": 1,
                "permission_id": 3,
            },
            {
                "role_id": 1,
                "permission_id": 4,
            },
            {
                "role_id": 1,
                "permission_id": 5,
            },
            {
                "role_id": 1,
                "permission_id": 6,
            },
            {
                "role_id": 2,
                "permission_id": 1,
            },
            {
                "role_id": 2,
                "permission_id": 2,
            },
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM permissions WHERE name IN ('USER_ADD', 'USER_DELETE')", execution_options=None)
