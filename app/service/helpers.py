import json
import uuid as uuid
from random import randint
from uuid import UUID

from requests import request

from app.config import get_settings

settings = get_settings()


def get_company_details(nip):

    url = f"https://rejestr.io/api/v1/krs?nip={nip}"

    payload = {}
    headers = {"Authorization": settings.api_rejestr_io}

    response = request("GET", url, headers=headers, data=payload)

    print(response.text)


def get_ip_info(ip):
    url = f"http://ipinfo.io/{ip}?token={settings.api_ipinfo}"
    response = "{'foo':'bar'}"
    if ip is not None:
        response = request("GET", url, headers={}, data={})

        if response.status_code != 200:
            return "Error code: " + str(response.status_code)
        return json.dumps(response.json())


def uuid_convert(o: uuid.uuid4) -> str:
    """Custom UUID converter for json.dumps(), because neither the UUID or the hex is a serializable object"""
    if isinstance(o, UUID):
        return o.hex


def get_uuid() -> uuid.uuid4:
    """Generate SQLModel safe UUID (without leading zero), https://github.com/tiangolo/sqlmodel/pull/26"""

    value = uuid.uuid4().hex
    if value[0] == "0":
        value.replace("0", str(randint(0, 9)), 1)

    value = str(randint(0, 9)) * (32 - len(value)) + value

    return value
