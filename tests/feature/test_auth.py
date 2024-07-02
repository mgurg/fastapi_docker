import json
from datetime import datetime

# from starlette.testclient import TestClient
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from loguru import logger


@pytest.mark.skip(reason="Function not implemented yet")
def test_account_limit(publicClient: TestClient):
    response = publicClient.request("GET", "/auth/account_limit", headers={"tenant": "public"})
    data = response.json()
    assert response.status_code == 200
    assert data["accounts"]
    assert data["limit"]


# def test_company_info(publicClient: TestClient):

#     result = {
#         "9542752600": {
#             "name": "Piekarnia - Cukiernia Bończyk Spółka Jawna",
#             "short_name": "Piekarnia - Cukiernia Bończyk Sp. J.",
#             "street": "Mysłowicka 40",
#             "postcode": "40-487",
#             "city": "Katowice",
#             "country_code": "PL",
#         },
#         "8981962322": {
#             "name": "Midea Spółka Z Ograniczoną Odpowiedzialnością",
#             "short_name": "Midea Sp. Z O. O.",
#             "street": "Gen. tadeusza kutrzeby 14",
#             "postcode": "52-213",
#             "city": "Wrocław",
#             "country_code": "PL",
#         },
#     }

#     keys = []
#     for key, value in result.items():
#         keys.append(key)

#     company_NIP = random.choice(keys)
#     data = {"country": "pl", "company_tax_id": company_NIP}

#     headers = {"tenant": "public", "Content-Type": "application/json"}
#     response = publicClient.request("POST","/auth/company_info", content=json.dumps(data), headers=headers)
#     data = response.json()

#     logger.error(data)
#     assert response.status_code == 200
#     assert data["name"] == result[company_NIP]["name"]
#     assert data["short_name"] == result[company_NIP]["short_name"]
#     assert data["street"] == result[company_NIP]["street"]
#     assert data["postcode"] == result[company_NIP]["postcode"]
#     assert data["city"] == result[company_NIP]["city"]
#     assert data["country_code"] == result[company_NIP]["country_code"]


@pytest.mark.skip(reason="Function not implemented yet")
def test_register(publicClient: TestClient):
    fake = Faker()

    data = {
        "first_name": "faker_000_" + fake.first_name(),
        "last_name": "faker_000_" + fake.last_name(),
        "email": "faker_000_@email.com",
        "password": "fake__password_string",
        "password_confirmation": "fake__password_string",
        "country": "pl",
        "company_tax_id": "8981962322",
        "company_name": "faker_000_" + fake.company(),
        "company_street": "faker_000_" + fake.street_name(),
        "company_city": "faker_000_" + fake.city(),
        "company_postcode": "string",
        "company_info_changed": True,
        "is_visible": True,
        "tos": True,
        "tz": "Europe/Warsaw",
        "lang": "pl",
    }
    headers = {"tenant": "public", "Content-Type": "application/json"}
    response = publicClient.request("POST", "/auth/register", content=json.dumps(data), headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["ok"] == True


@pytest.mark.skip(reason="Function not implemented yet")
def test_first_run(publicClient: TestClient):
    Faker()
    today = datetime.now().strftime("%A-%Y-%m-%d-%H")
    service_token = ("a" * int(64 - len(today))) + today

    data = {"token": service_token}
    headers = {"tenant": "public", "Content-Type": "application/json"}
    response = publicClient.request("POST", "/auth/first_run", content=json.dumps(data), headers=headers)
    data = response.json()

    a = {
        "ok": True,
        "first_name": "faker_000_Jeffrey",
        "last_name": "faker_000_Bray",
        "lang": "pl",
        "tz": "Europe/Warsaw",
        "uuid": "54495797-032c-4459-8dfb-7a0430235b78",
        "tenant_id": "fake_tenant_company_for_test_00000000000000000000000000000000",
        "token": "f8bcde19e66b142908af6afe4617f5e29b0eaf5b6a4717b9210d0d6e18b5731b",
    }

    # logger.error(data)
    assert response.status_code == 200
    assert data["ok"] == True
    assert data["lang"] == "pl"
    assert data["tz"] == "Europe/Warsaw"
    assert data["tenant_id"] == "fake_tenant_company_for_test_00000000000000000000000000000000"


@pytest.mark.skip(reason="Function not implemented yet")
def test_login(publicClient: TestClient):
    data = {"email": "faker_000_@email.com", "password": "fake__password_string", "permanent": True}

    headers = {"tenant": "public", "Content-Type": "application/json"}
    response = publicClient.request("POST", "/auth/login", content=json.dumps(data), headers=headers)
    data = response.json()

    r = {
        "auth_token": "bac8bc28bb876713c3daf391898e2142738851fb27aa9d3ff54e870954fc154c20973c00d0276e8417f13f444629f35d304f49abe5d97e68c0cda623833c5c96",
        "first_name": "faker_000_Cody",
        "last_name": "faker_000_Mata",
        "tz": "Europe/Warsaw",
        "lang": "pl",
        "uuid": "0204918a-b989-4869-bd29-674f1ded36de",
        "role_FK": {
            "role_name": "ADMIN_MASTER",
            "permission": [
                {"name": "USER_ADD"},
                {"name": "USER_EDIT"},
                {"name": "USER_DELETE"},
                {"name": "SETTINGS_IDEAS"},
                {"name": "SETTINGS_ROLES"},
                {"name": "SETTINGS_GROUPS"},
            ],
        },
        "tenant_id": "fake_tenant_company_for_test_00000000000000000000000000000000",
    }

    logger.error(data)
    assert response.status_code == 200
    assert data["auth_token"]
    assert data["first_name"]
    assert data["last_name"]
    assert data["tz"]
    assert data["lang"]
    assert data["uuid"]
    assert data["role_FK"]["role_name"] == "ADMIN_MASTER"
    assert data["role_FK"]["permission"][0]["name"]
