from datetime import datetime, timedelta

from faker import Faker
from fastapi.testclient import TestClient
from passlib.hash import argon2
from sqlalchemy import func
from sqlmodel import Session, select

from app.models.models import Tasks, Users
from app.service.helpers import get_uuid


def test_list_task(session: Session, client: TestClient):

    fake = Faker("pl_PL")
    for i in range(5):
        new_task = Tasks(
            uuid=get_uuid(),  # TODO 00000000-0000-0000-0000-000000000000
            client_id=2,
            author_id=1,
            title=fake.paragraph(nb_sentences=1),
            description=fake.paragraph(nb_sentences=5),
            date_from=datetime.utcnow(),
            date_to=datetime.utcnow(),
            priority="p1",
            type="t2",
            connected_tasks=1,
            created_at=datetime.utcnow(),
        )
        session.add(new_task)
        session.commit()

    response = client.get("/tasks/index")
    data = response.json()

    assert response.status_code == 200


def test_get_task(session: Session, client: TestClient):

    fake = Faker("pl_PL")
    for i in range(5):
        new_task = Tasks(
            uuid=get_uuid(),
            client_id=2,
            author_id=1,
            title=fake.paragraph(nb_sentences=1),
            description=fake.paragraph(nb_sentences=5),
            date_from=datetime.utcnow(),
            date_to=datetime.utcnow(),
            priority="p1",
            type="t2",
            connected_tasks=1,
            created_at=datetime.utcnow(),
        )
        session.add(new_task)
        session.commit()

    task = session.exec(select(Tasks).order_by(func.random())).first()

    response = client.get("/tasks/" + str(task.uuid))
    data = response.json()

    assert response.status_code == 200
    assert data["uuid"] == str(task.uuid)
    assert data["title"] == task.title
    assert data["description"] == task.description
    assert data["priority"] == task.priority
    assert data["type"] == task.type


def test_add_task(session: Session, client: TestClient):

    fake = Faker("pl_PL")

    new_user = {
        "author_id": 1,
        "title": fake.paragraph(nb_sentences=1),
        "description": fake.paragraph(nb_sentences=1),
        "date_from": "2022-01-30T11:44:36.081Z",
        "date_to": "2022-01-30T11:44:36.081Z",
        "priority": "urgent",
        "type": "alert",
        "connected_tasks": 1,
    }

    response = client.post("/tasks/add", json=new_user)
    data = response.json()

    assert response.status_code == 200
    assert data["ok"] == True


def test_edit_task(session: Session, client: TestClient):

    fake = Faker("pl_PL")
    for i in range(5):
        new_task = Tasks(
            uuid=get_uuid(),
            client_id=2,
            author_id=1,
            title=fake.paragraph(nb_sentences=1),
            description=fake.paragraph(nb_sentences=5),
            date_from=datetime.utcnow(),
            date_to=datetime.utcnow(),
            priority="p1",
            type="t2",
            connected_tasks=1,
            created_at=datetime.utcnow(),
        )
        session.add(new_task)
        session.commit()

    task_uuid = session.exec(select(Tasks).order_by(func.random())).first()  # random row

    new_user = {
        "title": fake.paragraph(nb_sentences=1),
        "description": fake.paragraph(nb_sentences=5),
    }

    response = client.patch("/tasks/" + str(task_uuid.uuid), json=new_user)
    data = response.json()

    assert response.status_code == 200
    assert data["ok"] == True


def test_delete_task(session: Session, client: TestClient):

    fake = Faker("pl_PL")
    for i in range(5):
        new_task = Tasks(
            uuid=get_uuid(),
            client_id=2,
            author_id=1,
            title=fake.paragraph(nb_sentences=1),
            description=fake.paragraph(nb_sentences=5),
            date_from=datetime.utcnow(),
            date_to=datetime.utcnow(),
            priority="p1",
            type="t2",
            connected_tasks=1,
            created_at=datetime.utcnow(),
        )
        session.add(new_task)
        session.commit()

    task_uuid = session.exec(select(Tasks).order_by(func.random())).first()  # random row

    response = client.delete("/tasks/" + str(task_uuid.uuid))
    data = response.json()

    assert response.status_code == 200
    assert data["ok"] == True
