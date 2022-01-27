from datetime import datetime, timedelta

from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.models import Users
from app.service.helpers import get_uuid


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


def test_post_register_activate(session: Session, client: TestClient):

    fake = Faker("pl_PL")

    for i in range(5):
        email = fake.email()
        token = fake.hexify("^" * 32)

        new_user = Users(
            client_id=fake.random_digit(),
            email=email,
            service_token=token,
            service_token_valid_to=datetime.now() + timedelta(days=1),
            password="pass_hash",
            user_role_id=2,
            created_at=datetime.utcnow(),
            is_active=False,
            tz=fake.timezone(),
            lang=fake.language_code(),
            uuid=get_uuid(),
        )
        session.add(new_user)
        session.commit()

    response = client.get("register/activate/" + token)
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == email
