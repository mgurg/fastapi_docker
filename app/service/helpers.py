import json
import uuid as uuid
from uuid import UUID

from requests import request

from app.config import get_settings

settings = get_settings()


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
