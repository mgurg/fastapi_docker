from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_main():
    response = client.request("GET", "/")
    assert response.status_code == 200
    # assert response.json() == {"Hello": "World"}
