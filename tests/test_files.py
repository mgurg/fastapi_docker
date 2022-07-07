# from datetime import datetime, timedelta

# from faker import Faker
# from fastapi.testclient import TestClient
# from passlib.hash import argon2
# from sqlalchemy import func
# from sqlmodel import Session, select

# from app.models.models import Files
# from app.service.helpers import get_uuid


# def test_list_files(session: Session, client: TestClient):

#     fake = Faker("pl_PL")
#     for i in range(5):
#         new_file = Files(
#             uuid=str(uuid.uuid4()),  # TODO 00000000-0000-0000-0000-000000000000
#             account_id=2,
#             owner_id=1,
#             file_name=fake.word(),
#             extension=fake.file_extension(),
#             mimetype=fake.mime_type(category="image"),
#             size=fake.random_digit_not_null(),
#             created_at=datetime.utcnow(),
#         )
#         session.add(new_file)
#         session.commit()

#     response = client.get("/files/index")
#     data = response.json()

#     assert response.status_code == 200


# def test_get_file(session: Session, client: TestClient):

#     fake = Faker("pl_PL")
#     for i in range(5):
#         new_file = Files(
#             uuid=str(uuid.uuid4()),  # TODO 00000000-0000-0000-0000-000000000000
#             account_id=2,
#             owner_id=1,
#             file_name=fake.word(),
#             extension=fake.file_extension(),
#             mimetype=fake.mime_type(category="image"),
#             size=fake.random_digit_not_null(),
#             created_at=datetime.utcnow(),
#         )
#         session.add(new_file)
#         session.commit()

#     file = session.exec(select(Files).order_by(func.random())).first()

#     response = client.get("/files/" + str(file.uuid))
#     data = response.json()

#     assert response.status_code == 200
#     assert data["uuid"] == str(file.uuid)
#     assert data["file_name"] == file.file_name
#     assert data["extension"] == file.extension
#     assert data["mimetype"] == file.mimetype
#     assert data["size"] == file.size
#     # url: HttpUrl
