import json
from io import BytesIO

from fastapi.testclient import TestClient
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK


def test_should_return_count_of_issues_by_type(client: TestClient):
    response = client.request(
        "GET", "/statistics_test/issues_counter",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    expected_data = {'accepted': 0, 'assigned': 0, 'done': 0, 'in_progress': 0, 'new': 0, 'paused': 0, 'rejected': 0}

    assert response.status_code == HTTP_200_OK
    assert data == expected_data


def test_should_return_count_of_issues_by_type(client: TestClient):
    response = client.request(
        "GET", "/statistics_test/first_steps",
        headers={"tenant": "fake_tenant_company_for_test_00000000000000000000000000000000"}
    )
    data = response.json()

    expected_data = {'favourites': 0,
                     'issues_active': {'me': 0, 'total': 0},
                     'issues_inactive': {'me': 0, 'total': 0},
                     'items': {'me': 0, 'total': 0},
                     'users': 2}

    assert response.status_code == HTTP_200_OK
    assert data == expected_data
