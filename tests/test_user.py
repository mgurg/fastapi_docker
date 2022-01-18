import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db import get_session
from app.main import app


def test_create_user(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    response = client.post("usr/add", json={"client_id": "Deadpond", "email": "mm@nn.pl"})
    app.dependency_overrides.clear()
    data = response.json()

    assert response.status_code == 200
    # assert data["name"] == "Deadpond"
    # assert data["secret_name"] == "Dive Wilson"
    # assert data["age"] is None
    # assert data["id"] is not None


def test_get_user(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)

    response = client.get("/usr/users")
    app.dependency_overrides.clear()
    data = response.json()

    assert response.status_code == 200
    # assert data["name"] == "Deadpond"
    # assert data["secret_name"] == "Dive Wilson"
    # assert data["age"] is None
    # assert data["id"] is not None
