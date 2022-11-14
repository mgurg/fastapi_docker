from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.orm import Session


def test_get_users(session: Session, client: TestClient):
    response = client.request(
        "GET", "/users", headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    r = {
        "items": [
            {
                "first_name": "faker_000_Thomas",
                "last_name": "faker_000_Franklin",
                "email": "faker_000_@email.com",
                "phone": None,
                "uuid": "ef37fb58-98aa-4a85-8901-5b63a0c3563b",
                "is_active": True,
                "is_verified": True,
                "role_FK": {
                    "uuid": "e255f78e-704f-4046-b1d7-89bb83786fef",
                    "role_name": "ADMIN_MASTER",
                    "role_title": "Main admin",
                },
            }
        ],
        "total": 1,
        "page": 1,
        "size": 50,
    }
    data = response.json()
    logger.error(data)
    assert response.status_code == 200
    assert data["items"]
    assert data["total"]
    assert data["page"]
    assert data["size"]
    assert data["items"][0]["first_name"]
    assert data["items"][0]["last_name"]
    assert data["items"][0]["email"]
    # assert data["items"][0]["phone"]
    assert data["items"][0]["uuid"]
    assert data["items"][0]["is_active"]
    assert data["items"][0]["is_verified"]
    assert data["items"][0]["role_FK"]
    assert data["items"][0]["role_FK"]["uuid"]
    assert data["items"][0]["role_FK"]["role_name"]
    assert data["items"][0]["role_FK"]["role_title"]


# TODO role_uuid
# def test_add_users(session: Session, client: TestClient):

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
#     headers = {"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000", "Content-Type": "application/json"}
#     response = client.request("POST","/users/", data=json.dumps(data), headers=headers)
#     data = response.json()
#     logger.info(data)
#     assert response.status_code == 200


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

#     response = client.request("PATCH","/users/" + str(user.uuid), data=json.dumps(data), headers=headers)
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
