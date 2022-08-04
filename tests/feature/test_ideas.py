import json

from faker import Faker
from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.models import Idea


def test_get_ideas(session: Session, client: TestClient):
    response = client.get("/ideas", headers={"tenant": "a"})
    data = response.json()
    assert response.status_code == 200


def test_add_ideas(session: Session, client: TestClient):

    fake = Faker()

    data = {
        "title": fake.text(max_nb_chars=20),
        "description": fake.paragraph(nb_sentences=1),
        "color": fake.safe_color_name(),
    }
    headers = {"tenant": "a", "Content-Type": "application/json"}
    response = client.post("/ideas/", data=json.dumps(data), headers=headers)
    data = response.json()
    logger.info(data)
    assert response.status_code == 200


def test_get_idea(session: Session, client: TestClient):
    user = session.execute(select(Idea).order_by(func.random()).limit(1)).scalar_one()
    response = client.get("/ideas/" + str(user.uuid), headers={"tenant": "a"})
    data = response.json()
    assert response.status_code == 200
    assert data["color"] == user.color
    assert data["title"] == user.title
    assert data["description"] == user.description
    assert data["uuid"] == str(user.uuid)


def test_delete_user(session: Session, client: TestClient):
    user = session.execute(select(Idea).order_by(func.random()).limit(1)).scalar_one()
    logger.info(user.uuid)
    response = client.delete("/ideas/" + str(user.uuid), headers={"tenant": "a"})
    data = response.json()
    logger.info(data)
    # {'ok': True}
    assert response.status_code == 200
