from datetime import datetime, timedelta
from uuid import UUID, uuid4

from faker import Faker
from fastapi.testclient import TestClient
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import TaskCreateFactory, Tasks, Users

# def test_add_single_task(session: Session, client: TestClient):

#     fake = Faker("pl_PL")

#     for i in range(5):
#         email = fake.email()
#         token = fake.hexify("^" * 32)
#         uuid = str(uuid4())

#         new_user = Users(
#             account_id=2,
#             email=email,
#             first_name=fake.first_name(),
#             last_name=fake.last_name(),
#             service_token=token,
#             service_token_valid_to=datetime.utcnow() + timedelta(days=1),
#             password=argon2.hash(fake.password()),
#             user_role_id=2,
#             created_at=datetime.utcnow(),
#             is_active=True,
#             is_verified=True,
#             tz=fake.timezone(),
#             lang=fake.language_code(),
#             uuid=uuid,
#         )
#         session.add(new_user)
#         session.commit()

#     # assignee = session.exec(select(Users).order_by(func.random())).first()

#     single_task = {
#         "assignee": str(uuid),
#         "title": fake.paragraph(nb_sentences=1),
#         "description": fake.paragraph(nb_sentences=1),
#         "is_active": True,
#         "priority": "urgent",
#         "type": "alert",
#         "recurring": False,
#         "color": fake.safe_color_name(),
#     }

#     response = client.post("/tasks/add", json=single_task)
#     data = response.json()

#     assert response.status_code == 200
#     assert data["ok"] == True


# def test_add_planned_task(session: Session, client: TestClient):

#     fake = Faker("pl_PL")

#     for i in range(5):
#         email = fake.email()
#         token = fake.hexify("^" * 32)
#         uuid = str(uuid4())

#         new_user = Users(
#             account_id=2,
#             email=email,
#             first_name=fake.first_name(),
#             last_name=fake.last_name(),
#             service_token=token,
#             service_token_valid_to=datetime.utcnow() + timedelta(days=1),
#             password=argon2.hash(fake.password()),
#             user_role_id=2,
#             created_at=datetime.utcnow(),
#             is_active=True,
#             is_verified=True,
#             tz=fake.timezone(),
#             lang=fake.language_code(),
#             uuid=uuid,
#         )
#         session.add(new_user)
#         session.commit()

#     assignee = session.exec(select(Users).order_by(func.random())).first()

#     planned_task = {
#         "assignee": str(uuid),
#         "title": fake.paragraph(nb_sentences=1),
#         "description": fake.paragraph(nb_sentences=1),
#         "is_active": True,
#         "priority": "urgent",
#         "type": "alert",
#         "recurring": False,
#         "color": fake.safe_color_name(),  # New:
#         "date_from": "2022-01-30T11:44:36.081Z",
#         "date_to": "2022-01-30T11:44:36.081Z",
#         "time_from": "11:44:36.081Z",
#         "time_to": "11:44:36.081Z",
#         "all_day": False,
#     }

#     response = client.post("/tasks/add", json=planned_task)
#     data = response.json()

#     assert response.status_code == 200
#     assert data["ok"] == True


# def test_add_recurring_task(session: Session, client: TestClient):

#     fake = Faker("pl_PL")

#     for i in range(5):
#         email = fake.email()
#         token = fake.hexify("^" * 32)
#         uuid = str(uuid4())

#         new_user = Users(
#             account_id=2,
#             email=email,
#             first_name=fake.first_name(),
#             last_name=fake.last_name(),
#             service_token=token,
#             service_token_valid_to=datetime.utcnow() + timedelta(days=1),
#             password=argon2.hash(fake.password()),
#             user_role_id=2,
#             created_at=datetime.utcnow(),
#             is_active=True,
#             is_verified=True,
#             tz=fake.timezone(),
#             lang=fake.language_code(),
#             uuid=uuid,
#         )
#         session.add(new_user)
#         session.commit()

#     assignee = session.exec(select(Users).order_by(func.random())).first()

#     recurring_task = {
#         "assignee": str(uuid),
#         "title": fake.paragraph(nb_sentences=1),
#         "description": fake.paragraph(nb_sentences=1),
#         "is_active": True,
#         "priority": "urgent",
#         "type": "alert",
#         "recurring": True,
#         "color": fake.safe_color_name(),
#         "date_from": "2022-01-30T11:44:36.081Z",
#         "date_to": "2022-01-30T11:44:36.081Z",
#         "time_from": "11:44:36.081Z",
#         "time_to": "11:44:36.081Z",
#         "all_day": False,
#         "interval": 1,
#         "freq": "DAILY",
#         "at_Mo": True,
#         "at_Tu": True,
#         "at_We": True,
#         "at_Th": True,
#         "at_Fr": True,
#         "at_Sa": True,
#         "at_Su": True,
#     }

#     response = client.post("/tasks/add", json=recurring_task)
#     data = response.json()

#     assert response.status_code == 200
#     assert data["ok"] == True


# def test_list_task(session: Session, client: TestClient):

#     tasks = TaskCreateFactory.batch(size=5)
#     for task in tasks:
#         session.add(task)
#         session.commit()
#         session.refresh(task)

#     response = client.get("/tasks/index")
#     data = response.json()
#     # print(data)
#     assert response.status_code == 200


# def test_get_task(session: Session, client: TestClient):

#     task = TaskCreateFactory.build()
#     task.uuid = "12daa1b3-5748-45ae-a9b6-5166f4946ac0"

#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     # task = session.exec(select(Tasks).order_by(func.random())).first()
#     task = session.exec(select(Tasks).where(Tasks.uuid == "12daa1b3-5748-45ae-a9b6-5166f4946ac0")).first()

#     response = client.get("/tasks/12daa1b3-5748-45ae-a9b6-5166f4946ac0")
#     data = response.json()

#     assert response.status_code == 200
#     assert data["uuid"] == str(task.uuid)
#     assert data["title"] == task.title
#     assert data["description"] == task.description
#     assert data["priority"] == task.priority
#     assert data["type"] == task.type


# def test_edit_single_task(session: Session, client: TestClient):

#     fake = Faker("pl_PL")

#     task = TaskCreateFactory.build()
#     # account.account_id = "EbLbndnlx4SZpgP3aB49SVWGNgE38qfXvl3LW"

#     session.add(task)
#     session.commit()
#     session.refresh(task)

#     task_uuid = session.exec(
#         select(Tasks).where(Tasks.recurring == False).where(Tasks.date_from == None).order_by(func.random())
#     ).first()  # random row

#     new_user = {
#         "title": fake.paragraph(nb_sentences=1),
#         "description": fake.paragraph(nb_sentences=5),
#     }

#     response = client.patch("/tasks/" + str(task_uuid.uuid), json=new_user)
#     data = response.json()

#     assert response.status_code == 200
#     assert data["ok"] == True


# def test_edit_planned_task(session: Session, client: TestClient):

#     fake = Faker("pl_PL")

#     task_uuid = session.exec(
#         select(Tasks).where(Tasks.recurring == False).where(Tasks.date_from != None).order_by(func.random())
#     ).first()  # random row

#     new_user = {
#         "title": fake.paragraph(nb_sentences=1),
#         "description": fake.paragraph(nb_sentences=5),
#         "date_from": "2022-03-30T11:44:36.081Z",
#         "date_to": "2022-03-30T11:44:36.081Z",
#         "time_from": "11:44:36.081Z",
#         "time_to": "11:44:36.081Z",
#         "all_day": False,
#     }

#     response = client.patch("/tasks/" + str(task_uuid.uuid), json=new_user)
#     data = response.json()

#     assert response.status_code == 200
#     assert data["ok"] == True


# def test_delete_task(session: Session, client: TestClient):

#     task_uuid = session.exec(select(Tasks).order_by(func.random())).first()  # random row

#     response = client.delete("/tasks/" + str(task_uuid.uuid))
#     data = response.json()

#     assert response.status_code == 200
#     assert data["ok"] == True
