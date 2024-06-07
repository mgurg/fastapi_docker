import json
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT

from app.models.models import Item


@pytest.fixture(scope="session")
def db_with_data(db_fixture: Session):
    # Create test data and insert it into the database
    item_data = {
        "uuid": str(uuid4()),
        'author_id': 2,
        "name": "Test Item",
        "symbol": "TI",
        "summary": "Test summary",
        "text": "<p>Test HTML</p>",
        "text_json": {"type": "doc",
                      "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test text"}]}]},
    }
    db_item = Item(**item_data)
    db_fixture.add(db_item)
    db_fixture.commit()
    return db_fixture


def test_should_return_all_items(client: TestClient):
    response = client.request(
        "GET", "/item_test?limit=10&offset=0",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    expected_data = {'count': 0, 'data': [], 'limit': 10, 'offset': 0}

    assert response.status_code == 200
    assert data == expected_data


def test_should_add_new_item_without_files(client: TestClient, db_fixture):
    data = {"name": "Narty", "symbol": "NO", "summary": "Some public summary",
            "text_html": "<p>HEAD - INDIGO PERFORMANCE [VT4] - Purism in perfection</p>",
            "text_json": {
                "type": "doc",
                "content": [{
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "HEAD - INDIGO PERFORMANCE [VT4] - Purism in perfection"}]}]},
            "files": []}

    response = client.request(
        "POST", "/item_test", content=json.dumps(data),
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    item = db_fixture.query(Item).filter(Item.name == "Narty").first()
    assert item is not None

    assert item.uuid is not None
    assert item.author_id is not None
    assert item.name == "Narty"
    assert item.summary == "Some public summary"
    assert item.symbol == "NO"
    assert item.text == "HEAD - INDIGO PERFORMANCE [VT4] - Purism in perfection"
    assert item.text_json == {"type": "doc", "content": [{"type": "paragraph", "content": [
        {"text": "HEAD - INDIGO PERFORMANCE [VT4] - Purism in perfection", "type": "text"}]}]}

    # Ensure the item is found in the database
    assert item is not None

    assert response.status_code == HTTP_201_CREATED
    assert data == {"ok": True}


def test_should_return_all_items(client: TestClient, db_with_data: Session):
    response = client.request(
        "GET", "/item_test?limit=10&offset=0",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    expected_data = {'count': 1,
                     'data': [
                         {'name': 'Test Item',
                          'text': '<p>Test HTML</p>',
                          'text_json':
                              {'content': [
                                  {'content': [
                                      {'text': 'Test text', 'type': 'text'}], 'type': 'paragraph'}],
                                  'type': 'doc'},
                          'uuid': '20102930-157e-4899-aedf-9a8866ca40a5'}],
                     'limit': 10,
                     'offset': 0}

    assert response.status_code == 200
    assert data["data"][0]['name'] == expected_data["data"][0]['name']
    assert data["data"][0]['text'] == expected_data["data"][0]['text']
    assert data["data"][0]['text_json'] == expected_data["data"][0]['text_json']


def test_should_export_all_items_to_csv(client: TestClient, db_with_data: Session):
    response = client.request(
        "GET", "/item_test/export",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )

    # Expected CSV content
    expected_csv = ('Name;Description;Symbol\r\n'
                    'Narty;HEAD - INDIGO PERFORMANCE [VT4] - Purism in perfection;NO\r\n'
                    'Test Item;<p>Test HTML</p>;TI\r\n')

    data = response.content.decode("utf-8")

    assert response.status_code == HTTP_200_OK
    # Assert headers
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "content-disposition" in response.headers
    assert response.headers["content-disposition"].startswith("attachment; filename=items_")
    assert response.headers["content-disposition"].endswith(".csv")

    # Assert CSV content
    assert data == expected_csv

# def test_should_import_all_items_from_csv(client: TestClient):
#     csv_content = b"""Id;Name;Email\n1;Alice;alice@example.com\n2;Bob;bob@example.com\n"""
#     file = BytesIO(csv_content)
#     file.seek(0)
#
#     response = client.request(
#         "POST", "/user_test/import", files={"file": ("test.csv", file, "text/csv")},
#         headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
#     )
#
#     data = response.json()
#
#     assert response.status_code == HTTP_200_OK
#     assert len(data) == 2
#     assert data["0"]["Name"] == "Alice"
#     assert data["0"]["Email"] == "alice@example.com"
#     assert data["0"]["uuid"] is not None
#     assert data["0"]["is_active"] is True
#     assert data["0"]["is_verified"] is True
#     assert data["0"]["tz"] == "Europe/Warsaw"
#     assert data["0"]["lang"] == "pl"
#     assert data["0"]["phone"] is None
#
#     assert data["1"]["Name"] == "Bob"
#     assert data["1"]["Email"] == "bob@example.com"
#     assert data["1"]["uuid"] is not None
#     assert data["1"]["is_active"] is True
#     assert data["1"]["is_verified"] is True
#     assert data["1"]["tz"] == "Europe/Warsaw"
#     assert data["1"]["lang"] == "pl"
#     assert data["1"]["phone"] is None


# def test_should_edit_existing_item(client: TestClient):
#     data = {
#         "first_name": "Jan",
#         "last_name": "Kowalski",
#         "email": "jk@example.com",
#         "phone": "2231478",
#         "password": "string",
#         "password_confirmation": "string",
#         "role_uuid": "758fb334-fe25-40b6-9ac4-98417522afd7"
#     }
#
#     response = client.request(
#         "PATCH", "/user_test/59e49dd8-efb0-4201-b767-607257fd13de", content=json.dumps(data),
#         headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
#     )
#     # data = response.json()
#
#     assert response.status_code == HTTP_200_OK

#
def test_should_delete_item(client: TestClient, db_fixture):
    item = db_fixture.query(Item).first()

    response = client.request(
        "DELETE", f"/item_test/{item.uuid}",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )

    assert response.status_code == HTTP_204_NO_CONTENT
