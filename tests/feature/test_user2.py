import json

from fastapi.testclient import TestClient


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


def test_should_return_count_of_all_users(client: TestClient):
    response = client.request(
        "GET", "/user_test?/count",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data['count'] == 2


def test_should_add_new_user(client: TestClient):
    data = {
        "first_name": "httpAPIUser",
        "last_name": "string",
        "email": "httpAPIUser@example.com",
        "phone": "string",
        "password": "string",
        "password_confirmation": "string",
        "is_verified": True,
        "user_role_uuid": "758fb334-fe25-40b6-9ac4-98417522afd7"
    }

    response = client.request(
        "POST", "/user_test", content=json.dumps(data),
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    assert response.status_code == 200
