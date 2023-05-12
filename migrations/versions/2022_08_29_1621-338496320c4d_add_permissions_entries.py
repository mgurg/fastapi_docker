"""Add Permissions Entries

Revision ID: 338496320c4d
Revises: 80726328353e
Create Date: 2022-08-29 16:21:50.746079

"""
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import table

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
        sa.Column("is_visible", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )

    permissions_dict = [
        # USERS
        {
            "uuid": uuid4(),
            "name": "OWNER_ACCESS",
            "title": "Master permission",
            "description": "Master permission",
            "group": "service",
            "is_visible": False,
        },
        {
            "uuid": uuid4(),
            "name": "USER_VIEW",
            "title": "Show users list",
            "description": "User can view list of other users",
            "group": "users",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "USER_ADD",
            "title": "Adding users",
            "description": "User can create new user accounts",
            "group": "users",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "USER_EDIT",
            "title": "Users editing",
            "description": "User can edit other users accounts",
            "group": "users",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "USER_EDIT_SELF",
            "title": "Account editing",
            "description": "Allow to edit my user account",
            "group": "users",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "USER_DELETE",
            "title": "Removing users",
            "description": "User can delete others users accounts",
            "group": "users",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "USER_IMPORT",
            "title": "Importing users",
            "description": "User can import  users data from CSV file",
            "group": "users",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "USER_EXPORT",
            "title": "Exporting users",
            "description": "User can export users data to CSV",
            "group": "users",
            "is_visible": True,
        },
        # ISSUES
        {
            "uuid": uuid4(),
            "name": "ISSUE_VIEW",
            "title": "Show issues list",
            "description": "User can view list of issues",
            "group": "issues",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ISSUE_ADD",
            "title": "Adding issues",
            "description": "User can create new issues",
            "group": "issues",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ISSUE_EDIT",
            "title": "Issue editing",
            "description": "User can edit issue",
            "group": "issues",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ISSUE_DELETE",
            "title": "Removing issues",
            "description": "User can delete existing issues",
            "group": "issues",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ISSUE_EXCLUDE",
            "title": "Exclude issues",
            "description": "Exclude issues from statistics",
            "group": "issues",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ISSUE_MANAGE",
            "title": "Manage work",
            "description": "Allow to Start, Pause and Finish  work",
            "group": "issues",
            "is_visible": True,
        },
        # {
        #     "uuid": uuid4(),
        #     "name": "ISSUE_SHOw_SUMMARY",
        #     "title": "Show work summary",
        #     "description": "Show work summary for finished tasks",
        #     "group": "issues"
        # },
        {
            "uuid": uuid4(),
            "name": "ISSUE_SHOw_HISTORY",
            "title": "Show issue history",
            "description": "Show issue history graph",
            "group": "issues",
            "is_visible": True,
        },
        # {
        #     "uuid": uuid4(),
        #     "name": "ISSUE_COMMENTS",
        #     "title": "Show Issue Comments",
        #     "description": "Show Issue Timeline",
        #     "group": "issues"
        # },
        {
            "uuid": uuid4(),
            "name": "ISSUE_REPLACED_PARTS",
            "title": "Show replaced parts",
            "description": "Allow to show, add, remove list of replaced parts",
            "group": "issues",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ISSUE_EXPORT",
            "title": "Exporting users",
            "description": "User can export users data to CSV",
            "group": "issues",
            "is_visible": True,
        },
        # ITEMS
        {
            "uuid": uuid4(),
            "name": "ITEM_VIEW",
            "title": "Show items list",
            "description": "User can view list of items",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_ADD",
            "title": "Adding items",
            "description": "User can create new items",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_EDIT",
            "title": "Item editing",
            "description": "User can edit item",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_HIDE",
            "title": "Hide items",
            "description": "User can hide existing item",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_DELETE",
            "title": "Removing items",
            "description": "User can delete existing item",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_SHOW_QR",
            "title": "Show QR in Item",
            "description": "Show QR in Item",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_SHOw_HISTORY",
            "title": "Show item history",
            "description": "Show item history graph",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_IMPORT",
            "title": "Importing items",
            "description": "User can import items data from CSV file",
            "group": "items",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "ITEM_EXPORT",
            "title": "Exporting items",
            "description": "User can export items data to CSV",
            "group": "items",
            "is_visible": True,
        },
        # {
        #     "uuid": uuid4(),
        #     "name": "ITEM_COMMENTS",
        #     "title": "Show Item comments",
        #     "description": "Show Item comments",
        #     "group": "items"
        # },
        # TAGS
        {
            "uuid": uuid4(),
            "name": "TAG_ADD",
            "title": "Add tag",
            "description": "Add tag",
            "group": "tags",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "TAG_EDIT",
            "title": "Edit tag",
            "description": "Edit tag",
            "group": "tags",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "TAG_HIDE",
            "title": "Hide tag",
            "description": "Hide tag",
            "group": "tags",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "TAG_DELETE",
            "title": "Delete tag",
            "description": "Delete tag",
            "group": "tags",
            "is_visible": True,
        },
        # SETTINGS
        {
            "uuid": uuid4(),
            "name": "SETTINGS_ACCOUNT",
            "title": "Acces to Account Settings",
            "description": "User can change account related settings",
            "group": "settings",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "SETTINGS_TAGS",
            "title": "Acces to Tags Settings",
            "description": "User can change Tags related settings",
            "group": "settings",
            "is_visible": True,
        },
        {
            "uuid": uuid4(),
            "name": "SETTINGS_PERMISSION",
            "title": "Acces to Permissions Settings",
            "description": "User can change Permission related settings",
            "group": "settings",
            "is_visible": True,
        },
    ]

    op.bulk_insert(permissions, permissions_dict)

    roles = table(
        "roles",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True, index=True),
        sa.Column("is_custom", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("is_visible", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("is_system", sa.BOOLEAN(), autoincrement=False, nullable=True, default=False),
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
                "is_system": True,
                "role_name": "ADMIN_MASTER",
                "role_title": "Main admin",
                "role_description": "Main admin role",
            },
            {
                "uuid": uuid4(),
                "is_custom": False,
                "is_visible": True,
                "is_system": False,
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

    # op.bulk_insert(
    #     roles_permissions_link,
    #     [
    #         {"role_id": 1, "permission_id": 1},
    #         {"role_id": 1, "permission_id": 2},
    #         {"role_id": 1, "permission_id": 3},
    #         {"role_id": 1, "permission_id": 4},
    #         {"role_id": 1, "permission_id": 5},
    #         {"role_id": 1, "permission_id": 6},
    #         {"role_id": 2, "permission_id": 1},
    #         {"role_id": 2, "permission_id": 2},
    #     ],
    # )

    admin_master_permissions: list[int] = list(range(1, len(permissions_dict) + 1))  # ALL: 1 ..32
    admin_permissions: list[int] = list(range(2, len(permissions_dict) + 1))
    role_permission_rel: dict = {1: admin_master_permissions, 2: admin_permissions}

    role_permission_rel_dict = []
    for key, values in role_permission_rel.items():
        # print(key, "->", values)

        for value in values:
            role_permission_rel_dict.append({"role_id": key, "permission_id": value})

    # print(role_permission_rel_dict)
    op.bulk_insert(roles_permissions_link, role_permission_rel_dict)


def downgrade() -> None:
    op.execute("DELETE FROM permissions WHERE name IN ('USER_ADD', 'USER_DELETE')", execution_options=None)
