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
    except Exception as e:
        raise

    # Search by NIP
    result = api.searchData(nip=nip)
    # pprint(result)

    data = {}
    data["name"] = result[0]["Nazwa"]
    data["short_name"] = result[0]["Nazwa"]
    data["nip"] = result[0]["Nip"]
    data["country"] = "Polska"
    data["city"] = result[0]["Miejscowosc"]

    # print(data)

    return data
