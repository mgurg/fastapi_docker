import json
import random

# from starlette.testclient import TestClient
import alembic
import alembic.config  # pylint: disable=E0401
import alembic.migration  # pylint: disable=E0401
import alembic.runtime.environment  # pylint: disable=E0401
import alembic.script  # pylint: disable=E0401
import alembic.util  # pylint: disable=E0401
from faker import Faker
from fastapi.testclient import TestClient
from loguru import logger


def test_account_limit(publicClient: TestClient):
    response = publicClient.get("/auth/account_limit", headers={"tenant": "public"})
    data = response.json()
    assert response.status_code == 200
    assert data["accounts"]
    assert data["limit"]


def test_company_info(publicClient: TestClient):

    result = {
        "9542752600": {
            "name": "Piekarnia - Cukiernia Bończyk Spółka Jawna",
            "short_name": "Piekarnia - Cukiernia Bończyk Sp. J.",
            "street": "Mysłowicka 40",
            "postcode": "40-487",
            "city": "Katowice",
            "country_code": "PL",
        },
        "8981962322": {
            "name": "Midea Spółka Z Ograniczoną Odpowiedzialnością",
            "short_name": "Midea Sp. Z O. O.",
            "street": "Gen. tadeusza kutrzeby 14",
            "postcode": "52-213",
            "city": "Wrocław",
            "country_code": "PL",
        },
    }

    keys = []
    for key, value in result.items():
        keys.append(key)

    company_NIP = random.choice(keys)
    data = {"country": "pl", "company_tax_id": company_NIP}

    headers = {"tenant": "public", "Content-Type": "application/json"}
    response = publicClient.post("/auth/company_info", data=json.dumps(data), headers=headers)
    data = response.json()

    logger.error(data)
    assert response.status_code == 200
    assert data["name"] == result[company_NIP]["name"]
    assert data["short_name"] == result[company_NIP]["short_name"]
    assert data["street"] == result[company_NIP]["street"]
    assert data["postcode"] == result[company_NIP]["postcode"]
    assert data["city"] == result[company_NIP]["city"]
    assert data["country_code"] == result[company_NIP]["country_code"]


def test_register(publicClient: TestClient):

    fake = Faker()

    data = {
        "first_name": "faker_000_" + fake.first_name(),
        "last_name": "faker_000_" + fake.last_name(),
        "email": "faker_000_" + fake.ascii_email(),
        "password": "string",
        "password_confirmation": "string",
        "country": "pl",
        "company_tax_id": "8981962322",
        "company_name": "faker_000_" + fake.company(),
        "company_street": "string",
        "company_city": "string",
        "company_postcode": "string",
        "company_info_changed": True,
        "tos": True,
        "tz": "Europe/Warsaw",
        "lang": "pl",
    }
    headers = {"tenant": "public", "Content-Type": "application/json"}
    response = publicClient.post("/auth/register", data=json.dumps(data), headers=headers)
    data = response.json()

    logger.error(data)
    assert response.status_code == 200
