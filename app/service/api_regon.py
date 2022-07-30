from pprint import pprint

from RegonAPI import RegonAPI
from RegonAPI.exceptions import ApiAuthenticationError

from app.config import get_settings

settings = get_settings()


def get_company_details(nip="7342867148"):

    # Authentication
    api = RegonAPI(bir_version="bir1.1", is_production=False, timeout=10, operation_timeout=10)
    try:
        api.authenticate(key=settings.GUS_API_DEV)
    except ApiAuthenticationError as e:
        print("[-]", e)
        exit(0)
    except Exception:
        raise

    # Search by NIP
    result = api.searchData(nip=nip)

    pprint(result)

    company_name: str = result[0].get("Nazwa", "noGusNameData")
    mapping = [
        ('"', ""),
        ("SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SP. Z O. O."),
        ("SPÓŁKA KOMANDYTOWA", "SP. K."),
        ("SPÓŁKA CYWILNA", "S.C."),
        ("SPÓŁKA JAWNA", "SP. J."),
        ("SPÓŁKA AKCYJNA", "SP. A."),
    ]
    for k, v in mapping:
        company_name_short = company_name.replace(k, v)

    data = {}
    data["name"] = company_name
    data["short_name"] = company_name_short
    data["nip"] = result[0].get("Nip")
    data["country"] = "Polska"
    data["city"] = result[0].get("Miejscowosc", "noGusCityData")

    # print(data)

    return data
