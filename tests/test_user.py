from datetime import datetime, timedelta

from faker import Faker
from fastapi.testclient import TestClient
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import Users
from app.service.helpers import get_uuid


def test_list_users(session: Session, client: TestClient):
    fake = Faker("pl_PL")

    for i in range(5):
        email = fake.email()
        token = fake.hexify("^" * 32)

        new_user = Users(
            account_id=fake.random_digit(),
            email=email,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            service_token=token,
            service_token_valid_to=datetime.utcnow() + timedelta(days=1),
            password=argon2.hash(fake.password()),
            user_role_id=2,
            created_at=datetime.utcnow(),
            is_active=True,
            is_verified=True,
            tz=fake.timezone(),
            lang=fake.language_code(),
            uuid=get_uuid(),
        )
        session.add(new_user)
        session.commit()

    response = client.get("user/")
    data = response.json()
    assert response.status_code == 200


# def test_get_user(session: Session, client: TestClient):
#     fake = Faker("pl_PL")

#     for i in range(5):
#         new_user = Users(
#             account_id=2,
#             email=fake.email(),
#             first_name=fake.first_name(),
#             last_name=fake.last_name(),
#             service_token=fake.hexify("^" * 32),
#             service_token_valid_to=datetime.utcnow() + timedelta(days=1),
#             password=argon2.hash(fake.password()),
#             user_role_id=2,
#             created_at=datetime.utcnow(),
#             is_active=True,
#             tz=fake.timezone(),
#             lang=fake.language_code(),
#             uuid=get_uuid(),
#         )
#         session.add(new_user)
#         session.commit()

#     user_uuid = session.exec(
#         select(Users).where(Users.is_active == True).where(Users.account_id == 2).order_by(func.random())
#     ).first()

#     response = client.get("user/" + str(user_uuid.uuid))
#     data = response.json()
#     assert response.status_code == 200
#     assert data["first_name"] == user_uuid.first_name
#     assert data["last_name"] == user_uuid.last_name
#     assert data["uuid"] == str(user_uuid.uuid)
