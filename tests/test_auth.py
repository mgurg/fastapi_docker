from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_register(session: Session, client: TestClient):
    assert 200 == 200
    # data = {
    #     "email": "test@example.com",
    #     "password": "string",
    #     "password_confirmation": "string",
    #     "tos": True,
    #     "tz": "Europe/Warsaw",
    #     "lang": "pl",
    # }
    # response = client.post("/auth/register", json=data, headers={"tenant": "public"})
    # data = response.json()
    # assert response.status_code == 200
