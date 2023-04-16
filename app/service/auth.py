import json
import re
import uuid as uuid
from uuid import UUID

import pytz
from disposable_email_domains import blocklist
from requests import request
from stdnum.pl import nip

from app.config import get_settings

settings = get_settings()


def is_email_temporary(email):
    return email.strip().split("@")[1] in blocklist


def is_timezone_correct(tz):
    return tz in pytz.all_timezones_set


def is_nip_correct(nipId):
    re.sub("[^0-9]", "", nipId)
    return nip.is_valid(nipId)


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
