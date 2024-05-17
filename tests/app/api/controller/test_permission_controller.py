import json
import uuid
from io import BytesIO

from fastapi.testclient import TestClient
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK


def test_should_return_all_permissions(client: TestClient):
    response = client.request(
        "GET", "/permission_test/all",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    def is_valid_uuid(value: str) -> bool:
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    expected_data = [
        {
            "group": "issues",
            "title": "Show issues list",
            "name": "ISSUE_VIEW",
            "description": "User can view list of issues"
        },
        {
            "group": "issues",
            "title": "Adding issues",
            "name": "ISSUE_ADD",
            "description": "User can create new issues"
        },
        {
            "group": "issues",
            "title": "Issue editing",
            "name": "ISSUE_EDIT",
            "description": "User can edit issue"
        },
        {
            "group": "issues",
            "title": "Removing issues",
            "name": "ISSUE_DELETE",
            "description": "User can delete existing issues"
        },
        {
            "group": "issues",
            "title": "Exclude issues",
            "name": "ISSUE_EXCLUDE",
            "description": "Exclude issues from statistics"
        },
        {
            "group": "issues",
            "title": "Manage work",
            "name": "ISSUE_MANAGE",
            "description": "Allow to Start, Pause and Finish  work"
        },
        {
            "group": "issues",
            "title": "Show issue history",
            "name": "ISSUE_SHOw_HISTORY",
            "description": "Show issue history graph"
        },
        {
            "group": "issues",
            "title": "Show replaced parts",
            "name": "ISSUE_REPLACED_PARTS",
            "description": "Allow to show, add, remove list of replaced parts"
        },
        {
            "group": "issues",
            "title": "Exporting users",
            "name": "ISSUE_EXPORT",
            "description": "User can export users data to CSV"
        },
        {
            "group": "items",
            "title": "Show items list",
            "name": "ITEM_VIEW",
            "description": "User can view list of items"
        },
        {
            "group": "items",
            "title": "Adding items",
            "name": "ITEM_ADD",
            "description": "User can create new items"
        },
        {
            "group": "items",
            "title": "Item editing",
            "name": "ITEM_EDIT",
            "description": "User can edit item"
        },
        {
            "group": "items",
            "title": "Hide items",
            "name": "ITEM_HIDE",
            "description": "User can hide existing item"
        },
        {
            "group": "items",
            "title": "Removing items",
            "name": "ITEM_DELETE",
            "description": "User can delete existing item"
        },
        {
            "group": "items",
            "title": "Show QR in Item",
            "name": "ITEM_SHOW_QR",
            "description": "Show QR in Item"
        },
        {
            "group": "items",
            "title": "Show item history",
            "name": "ITEM_SHOw_HISTORY",
            "description": "Show item history graph"
        },
        {
            "group": "items",
            "title": "Importing items",
            "name": "ITEM_IMPORT",
            "description": "User can import items data from CSV file"
        },
        {
            "group": "items",
            "title": "Exporting items",
            "name": "ITEM_EXPORT",
            "description": "User can export items data to CSV"
        },
        {
            "group": "service",
            "title": "Master permission",
            "name": "OWNER_ACCESS",
            "description": "Master permission"
        },
        {
            "group": "settings",
            "title": "Acces to Account Settings",
            "name": "SETTINGS_ACCOUNT",
            "description": "User can change account related settings"
        },
        {
            "group": "settings",
            "title": "Acces to Tags Settings",
            "name": "SETTINGS_TAGS",
            "description": "User can change Tags related settings"
        },
        {
            "group": "settings",
            "title": "Acces to Permissions Settings",
            "name": "SETTINGS_PERMISSION",
            "description": "User can change Permission related settings"
        },
        {
            "group": "tags",
            "title": "Add tag",
            "name": "TAG_ADD",
            "description": "Add tag"
        },
        {
            "group": "tags",
            "title": "Edit tag",
            "name": "TAG_EDIT",
            "description": "Edit tag"
        },
        {
            "group": "tags",
            "title": "Hide tag",
            "name": "TAG_HIDE",
            "description": "Hide tag"
        },
        {
            "group": "tags",
            "title": "Delete tag",
            "name": "TAG_DELETE",
            "description": "Delete tag"
        },
        {
            "group": "users",
            "title": "Show users list",
            "name": "USER_VIEW",
            "description": "User can view list of other users"
        },
        {
            "group": "users",
            "title": "Adding users",
            "name": "USER_ADD",
            "description": "User can create new user accounts"
        },
        {
            "group": "users",
            "title": "Users editing",
            "name": "USER_EDIT",
            "description": "User can edit other users accounts"
        },
        {
            "group": "users",
            "title": "Account editing",
            "name": "USER_EDIT_SELF",
            "description": "Allow to edit my user account"
        },
        {

            "group": "users",
            "title": "Removing users",
            "name": "USER_DELETE",
            "description": "User can delete others users accounts"
        },
        {
            "group": "users",
            "title": "Importing users",
            "name": "USER_IMPORT",
            "description": "User can import  users data from CSV file"
        },
        {
            "group": "users",
            "title": "Exporting users",
            "name": "USER_EXPORT",
            "description": "User can export users data to CSV"
        }
    ]

    assert response.status_code == 200
    assert len(data) == len(expected_data)

    for item, expected_item in zip(data, expected_data):
        assert is_valid_uuid(item["uuid"]), f"Invalid UUID: {item['uuid']}"
        for key in expected_item:
            assert item[key] == expected_item[
                key], f"Mismatch for key '{key}': expected '{expected_item[key]}', got '{item[key]}'"
