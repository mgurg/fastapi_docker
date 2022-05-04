from datetime import datetime, timedelta

from faker import Faker
from fastapi.testclient import TestClient
from passlib.hash import argon2
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

    response = client.post("auth/add", json=data)

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

    response = client.post("auth/add", json=data)
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Password and password confirmation not match"


def test_post_register_first_run(session: Session, client: TestClient):
    fake = Faker("pl_PL")

    for i in range(5):
        email = fake.email()
        token = fake.hexify("^" * 32)

        new_user = Users(
            account_id=fake.random_digit(),
            email=email,
            service_token=token,
            service_token_valid_to=datetime.utcnow() + timedelta(days=1),
            password=argon2.hash(fake.password()),
            user_role_id=2,
            created_at=datetime.utcnow(),
            is_active=False,
            tz=fake.timezone(),
            lang=fake.language_code(),
            uuid=get_uuid(),
        )
        session.add(new_user)
        session.commit()

    data = {"first_name": fake.first_name(), "last_name": fake.last_name(), "nip": fake.company_vat(), "token": token}

    response = client.post("auth/first_run", json=data)
    data = response.json()
    assert response.status_code == 200
    assert data["ok"] == True


# def test_post_login(session: Session, client: TestClient):
#     fake = Faker("pl_PL")

#     for i in range(5):
#         email = fake.email()
#         password = fake.password()
#         first_name = fake.first_name()
#         last_name = fake.last_name()
#         tz = fake.timezone()
#         lang = fake.language_code()

#         new_user = Users(
#             account_id=fake.random_digit(),
#             email=email,
#             first_name=first_name,
#             last_name=last_name,
#             service_token=None,
#             service_token_valid_to=None,
#             password=argon2.hash(password),
#             user_role_id=2,
#             created_at=datetime.utcnow(),
#             is_active=True,
#             tz=tz,
#             lang=lang,
#             uuid=get_uuid(),
#         )
#         session.add(new_user)
#         session.commit()

#     permanent = fake.boolean()
#     data = {"email": email, "password": password, "permanent": permanent}
#     headers = {"accept-language": fake.language_code(), "User-Agent": fake.user_agent()}

#     response = client.post("auth/login", json=data, headers=headers)
#     data = response.json()
#     assert response.status_code == 200
#     assert data["first_name"] == first_name
#     assert data["last_name"] == last_name
#     assert data["tz"] == tz
#     assert data["lang"] == lang


def test_post_verify(session: Session, client: TestClient):
    fake = Faker("pl_PL")

    for i in range(5):
        email = fake.email()
        password = fake.password()
        first_name = fake.first_name()
        last_name = fake.last_name()
        tz = fake.timezone()
        lang = fake.language_code()
        auth_token = fake.hexify("^" * 32)

        new_user = Users(
            account_id=fake.random_digit(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            service_token=None,
            service_token_valid_to=None,
            auth_token=auth_token,
            auth_token_valid_to=datetime.utcnow() + timedelta(days=1),
            password=argon2.hash(password),
            user_role_id=2,
            created_at=datetime.utcnow(),
            is_active=True,
            tz=tz,
            lang=lang,
            uuid=get_uuid(),
        )
        session.add(new_user)
        session.commit()

    response = client.get("auth/verify/" + auth_token)
    data = response.json()
    assert response.status_code == 200
    assert data["ok"] == True
