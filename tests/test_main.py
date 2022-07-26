from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

client = TestClient(app)


def test_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


# def test_tenant_create():
#     response = client.get("/create?name=a&schema=a&host=a")
#     assert response.status_code == 200
#     assert response.json() == {"name": "a", "schema": "a", "host": "a"}
#     assert True
