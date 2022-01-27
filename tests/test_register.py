from faker import Faker
from fastapi.testclient import TestClient


def test_post_register_ok(client: TestClient):
    fake = Faker("pl_PL")
    password = fake.password()

    data = {
        "email": fake.email(),
        "password": password,
        "password_confirmation": password,
        "tos": True,
        "tz": fake.timezone(),
        "lang": "pl_PL",
    }

    response = client.post("register/add", json=data)

    data = response.json()

    assert response.status_code == 200
    assert data["ok"] == True


def test_post_register_wrong_password(client: TestClient):
    fake = Faker("pl_PL")

    data = {
        "email": fake.email(),
        "password": fake.password(),
        "password_confirmation": fake.password(),
        "tos": True,
        "tz": fake.timezone(),
        "lang": "pl_PL",
    }

    response = client.post("register/add", json=data)
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Password and password confirmation not match"
