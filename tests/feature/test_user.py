import json

from faker import Faker
from fastapi.testclient import TestClient
from loguru import logger


def test_get_users(client: TestClient):
    response = client.request(
        "GET", "/users", headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    expected_data = {'items': [{'email': 'user@example.com',
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
                     'page': 1,
                     'pages': 1,
                     'size': 50,
                     'total': 2}

    assert response.status_code == 200
    assert data == expected_data


# TODO role_uuid
def test_add_users(client: TestClient):
    fake = Faker()

    password = fake.password()

    data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "password": password,
        "password_confirmation": password
        # "is_verified": True,
    }
    headers = {"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000",
               "Content-Type": "application/json"}
    response = client.request("POST", "/users/", content=json.dumps(data), headers=headers)
    data = response.json()
    logger.info(data)
    assert response.status_code == 200

# def test_edit_user(session: Session, client: TestClient):

#     fake = Faker()

#     password = fake.password()

#     data = {
#         "first_name": fake.first_name(),
#         "last_name": fake.last_name(),
#         "email": fake.email(),
#         "password": password,
#         "password_confirmation": password
#         # "is_verified": True,
#     }

#     user = session.execute(select(User).order_by(func.random()).limit(1)).scalar_one()
#     headers = {"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000", "Content-Type": "application/json"}

#     response = client.request("PATCH","/users/" + str(user.uuid), content=json.dumps(data), headers=headers)
#     data = response.json()
#     assert response.status_code == 200


# def test_get_user(session: Session, client: TestClient):
#     user = session.execute(select(User).order_by(func.random()).limit(1)).scalar_one()
#     response = client.request("GET","/users/" + str(user.uuid), headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"})
#     data = response.json()
#     assert response.status_code == 200
#     assert data["first_name"] == user.first_name
#     assert data["last_name"] == user.last_name
#     assert data["email"] == user.email
#     assert data["uuid"] == str(user.uuid)


# def test_delete_user(session: Session, client: TestClient):
#     user = session.execute(select(User).order_by(func.random()).limit(1)).scalar_one()
#     logger.info(user.uuid)
#     response = client.request("DELETE","/users/" + str(user.uuid), headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"})
#     data = response.json()
#     logger.info(data)
#     # {'ok': True}
#     assert response.status_code == 200
