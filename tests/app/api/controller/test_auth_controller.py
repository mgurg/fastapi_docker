import json
from io import BytesIO

from fastapi.testclient import TestClient
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK


def test_should_return_count_of_all_registered_accounts(client: TestClient):
    response = client.request("GET", "/auth_test/account_limit")
    data = response.json()

    assert response.status_code == 200
    assert data == {'accounts': 1, 'limit': 120}
