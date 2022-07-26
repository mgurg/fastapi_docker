import json
import re
from pathlib import Path

from app.config import get_settings

settings = get_settings()


def get_company_details(nip):
    nip = re.sub("[^0-9]", "", nip)
    url = "https://rejestr.io/api/v2/org?nip=" + nip
    headers = {"Authorization": settings.REJESTR_IO_KEY}

    path = Path(__file__).parent.parent.parent.joinpath("tests", "api_responses", "rejestr_io_get_by_nip.json")

    with path.open(encoding="UTF-8") as file:
        request_json = json.load(file)

    try:
        data = {}
        data["name"] = request_json["wyniki"][0]["nazwy"]["pelna"]
        data["short_name"] = request_json["wyniki"][0]["nazwy"]["skrocona"]
        data["nip"] = nip
        data["country"] = request_json["wyniki"][0]["adres"]["panstwo"]
        data["city"] = request_json["wyniki"][0]["adres"]["miejscowosc"]
    except Exception as e:
        print(e)

    # r = requests.get(url, headers=headers)
    # print(response.text)
    # if r.status_code != 200:
    #     print("error")

    # request_json = r.json()
    # print("")
    # print(request_json)

    return data
