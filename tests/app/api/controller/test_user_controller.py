import json
from io import BytesIO

from fastapi.testclient import TestClient
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK


def test_should_return_count_of_all_users(client: TestClient):
    response = client.request(
        "GET", "/user_test/count",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data == 2


def test_should_return_all_users(client: TestClient):
    response = client.request(
        "GET", "/user_test?limit=10&offset=0",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    expected_data = {'count': 2,
                     'data': [{'email': 'user@example.com',
                               'first_name': 'Jan',
                               'is_active': True,
                               'is_verified': True,
                               'last_name': 'Kowalski',
                               'phone': '',
                               'role_FK': {'role_name': 'ADMIN_MASTER',
                                           'role_title': 'Main admin',
                                           'uuid': 'a8cd3ea8-6a52-482d-9ca8-097d59429ea5'},
                               'uuid': '59e49dd8-efb0-4201-b767-607257fd13de'},
                              {'email': 'maciej.xxx@gmail.com',
                               'first_name': 'Maciej',
                               'is_active': True,
                               'is_verified': True,
                               'last_name': 'Nowak',
                               'phone': '',
                               'role_FK': {'role_name': 'Serwisant',
                                           'role_title': 'Serwisant',
                                           'uuid': '4b3be063-7cdd-434a-96c5-7de2a32d19d3'},
                               'uuid': '94ca4f7e-e4ae-4921-8758-94e672fe201d'}],
                     'limit': 10,
                     'offset': 0}

    assert response.status_code == 200
    assert data == expected_data


def test_should_return_main_admin(client: TestClient):
    response = client.request(
        "GET", "/user_test/59e49dd8-efb0-4201-b767-607257fd13de",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    expected_data = {'email': 'user@example.com',
                     'first_name': 'Jan',
                     'is_active': True,
                     'is_verified': True,
                     'last_name': 'Kowalski',
                     'phone': '',
                     'role_FK': {'role_name': 'ADMIN_MASTER',
                                 'role_title': 'Main admin',
                                 'uuid': 'a8cd3ea8-6a52-482d-9ca8-097d59429ea5'},
                     'uuid': '59e49dd8-efb0-4201-b767-607257fd13de'}

    assert response.status_code == 200
    assert data == expected_data


def test_should_add_new_user(client: TestClient):
    data = {
        "first_name": "httpAPIUser",
        "last_name": "string",
        "email": "httpAPIUser@example.com",
        "phone": "string",
        "password": "string",
        "password_confirmation": "string",
        "is_verified": True,
        "role_uuid": "758fb334-fe25-40b6-9ac4-98417522afd7"
    }

    response = client.request(
        "POST", "/user_test", content=json.dumps(data),
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    assert response.status_code == HTTP_201_CREATED


def test_should_export_all_users_to_csv(client: TestClient):
    response = client.request(
        "GET", "/user_test/export",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )

    # Expected CSV content
    expected_csv = ('First Name;Last Name;Email\r\n'
                    'Maciej;Nowak;maciej.xxx@gmail.com\r\n'
                    'httpAPIUser;string;httpAPIUser@example.com\r\n')

    data = response.content.decode("utf-8")

    assert response.status_code == HTTP_200_OK
    # Assert headers
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "content-disposition" in response.headers
    assert response.headers["content-disposition"].startswith("attachment; filename=users_")
    assert response.headers["content-disposition"].endswith(".csv")

    # Assert CSV content
    assert data == expected_csv


def test_should_import_all_users_from_csv(client: TestClient):
    csv_content = b"""Id;Name;Email\n1;Alice;alice@example.com\n2;Bob;bob@example.com\n"""
    file = BytesIO(csv_content)
    file.seek(0)

    response = client.request(
        "POST", "/user_test/import", files={"file": ("test.csv", file, "text/csv")},
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )

    data = response.json()

    assert response.status_code == HTTP_200_OK
    assert len(data) == 2
    assert data["0"]["Name"] == "Alice"
    assert data["0"]["Email"] == "alice@example.com"
    assert data["0"]["uuid"] is not None
    assert data["0"]["is_active"] is True
    assert data["0"]["is_verified"] is True
    assert data["0"]["tz"] == "Europe/Warsaw"
    assert data["0"]["lang"] == "pl"
    assert data["0"]["phone"] is None

    assert data["1"]["Name"] == "Bob"
    assert data["1"]["Email"] == "bob@example.com"
    assert data["1"]["uuid"] is not None
    assert data["1"]["is_active"] is True
    assert data["1"]["is_verified"] is True
    assert data["1"]["tz"] == "Europe/Warsaw"
    assert data["1"]["lang"] == "pl"
    assert data["1"]["phone"] is None


def test_should_edit_existing_user(client: TestClient):
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "email": "jk@example.com",
        "phone": "2231478",
        "password": "string",
        "password_confirmation": "string",
        "role_uuid": "758fb334-fe25-40b6-9ac4-98417522afd7"
    }

    response = client.request(
        "PATCH", "/user_test/59e49dd8-efb0-4201-b767-607257fd13de", content=json.dumps(data),
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    # data = response.json()

    assert response.status_code == HTTP_200_OK


def test_should_delete_user(client: TestClient):
    response = client.request(
        "DELETE", "/user_test/59e49dd8-efb0-4201-b767-607257fd13de",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )

    assert response.status_code == HTTP_204_NO_CONTENT
