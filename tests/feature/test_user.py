from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_users(session: Session, client: TestClient):
    response = client.get("/users", headers={"tenant": "a"})
    response.json()
    assert response.status_code == 200


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
#     headers = {"tenant": "a", "Content-Type": "application/json"}
#     response = client.post("/users/", data=json.dumps(data), headers=headers)
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
#     headers = {"tenant": "a", "Content-Type": "application/json"}

#     response = client.patch("/users/" + str(user.uuid), data=json.dumps(data), headers=headers)
#     data = response.json()
#     assert response.status_code == 200


# def test_get_user(session: Session, client: TestClient):
#     user = session.execute(select(User).order_by(func.random()).limit(1)).scalar_one()
#     response = client.get("/users/" + str(user.uuid), headers={"tenant": "a"})
#     data = response.json()
#     assert response.status_code == 200
#     assert data["first_name"] == user.first_name
#     assert data["last_name"] == user.last_name
#     assert data["email"] == user.email
#     assert data["uuid"] == str(user.uuid)


# def test_delete_user(session: Session, client: TestClient):
#     user = session.execute(select(User).order_by(func.random()).limit(1)).scalar_one()
#     logger.info(user.uuid)
#     response = client.delete("/users/" + str(user.uuid), headers={"tenant": "a"})
#     data = response.json()
#     logger.info(data)
#     # {'ok': True}
#     assert response.status_code == 200
