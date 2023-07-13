import json
import os
import re
import traceback
from pathlib import Path
from string import capwords

import requests
from loguru import logger
from pyVies import api
from RegonAPI import RegonAPI
from RegonAPI.exceptions import ApiAuthenticationError

from app.config import get_settings

settings = get_settings()

# https://stackoverflow.com/questions/48572494/structuring-api-calls-in-python
# https://github.com/sunkaflek/vies-parser


class CompanyDetails:
    def __init__(self, country: str, tax_id: str):
        self.country = country.upper()
        self.tax_id = re.sub("[^A-Za-z0-9]", "", tax_id)
        self.vat_eu = "".join([self.country, self.tax_id.upper()])

    def get_company_details(self):
        data = None
        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            logger.info("Company data test")
            return self.rejestr_io()

        try:
            if data is None:
                data = self.vies()
            if data is None:
                data = self.gus()
            if data is None:
                data = self.rejestr_io()
            if data is None:
                data = {
                    "name": "Nie znaleziono - uzupelnij",
                    "short_name": "Nie znaleziono - uzupelnij",
                    "street": "",
                    "postcode": "",
                    "city": "",
                    "country_code": "PL",
                }
        except Exception as e:
            print(e)
            traceback.print_exc()
            return None
        return data

    def vies(self):
        try:
            vies = api.Vies()
            result = vies.request(self.vat_eu, self.country, extended_info=True)

        except api.ViesValidationError as e:
            print("ViesValidationError", e)
            return None
        except api.ViesHTTPError as e:
            print("ViesHTTPError", e)
            return None
        except api.ViesError as e:
            print("ViesError", e)
            return None

        if result and (result["valid"] is False):  # 5691805989
            return None

        try:
            name = {
                "name": capwords(result["traderName"], sep=None),
                "short_name": self.get_company_short_name(company_name=result["traderName"]),
            }

            print(result["traderAddress"])
            address = self.get_vies_parsed_address(address=result["traderAddress"])
        except Exception:
            traceback.print_exc()
            return None
        if address is None:
            return None
        return name | address

    def gus(self):
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
        result = api.searchData(nip=self.tax_id)
        company_name: str = result[0].get("Nazwa")

        if company_name is None:
            return None

        mapping = [
            ('"', ""),
            ("SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SP. Z O. O."),
            ("SPÓŁKA KOMANDYTOWA", "SP. K."),
            ("SPÓŁKA CYWILNA", "S.C."),
            ("SPÓŁKA JAWNA", "SP. J."),
            ("SPÓŁKA AKCYJNA", "SP. A."),
        ]
        for k, v in mapping:
            company_name.replace(k, v)

        street = " ".join(
            [result[0].get("Ulica", ""), result[0].get("NrNieruchomosci", ""), result[0].get("NrLokalu", "")]
        )

        data = {
            "name": company_name,
            "short_name": self.get_company_short_name(company_name=company_name),
            "street": street,
            "postcode": result[0].get("KodPocztowy", ""),
            "city": result[0].get("Miejscowosc", ""),
            "country_code": self.vat_eu[:2],
        }

        return data

    def rejestr_io(self) -> dict | None:
        data = None
        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            logger.info("Company data test")
            path = Path(__file__).parent.parent.parent.joinpath("tests", "api_responses", "rejestr_io_get_by_nip.json")

            with path.open(encoding="UTF-8") as file:
                request_json = json.load(file)
            return {"message": "TEST_EMAIL_NOTIFICATION"}
        else:
            headers = {"Authorization": settings.REJESTR_IO_KEY}
            url = "https://rejestr.io/api/v2/org?nip=" + self.tax_id
            r = requests.get(url, headers=headers)
            # if r.status_code != 200:
            #     print("error")

            request_json = r.json()

        try:
            data = {
                "name": request_json["wyniki"][0]["nazwy"]["pelna"],
                "short_name": request_json["wyniki"][0]["nazwy"]["pelna"],
                "street": request_json["wyniki"][0]["adres"]["ulica"],
                "postcode": request_json["wyniki"][0]["adres"]["kod"],
                "city": request_json["wyniki"][0]["adres"]["miejscowosc"],
                "country_code": self.vat_eu[:2],
            }

        except Exception as e:
            print(e)

        return data

    @staticmethod
    def get_company_short_name(company_name):
        company_name = company_name.upper()

        mapping = [
            ('"', ""),
            ("SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ", "SP. Z O. O."),
            ("SPÓŁKA KOMANDYTOWA", "SP. K."),
            ("SPÓŁKA CYWILNA", "S.C."),
            ("SPÓŁKA JAWNA", "SP. J."),
            ("SPÓŁKA AKCYJNA", "SP. A."),
        ]
        for k, v in mapping:
            company_name = company_name.replace(k, v)

        return capwords(company_name, sep=None)

    @staticmethod
    def get_vies_supported_countries():
        return ["SK", "NL", "BE", "FR", "PT", "IT", "FI", "RO", "SI", "AT", "PL", "HR", "EL", "DK", "EE", "CZ"]

    def get_vies_parsed_address(self, address) -> dict | None:
        country_code = self.vat_eu[:2]
        newlines = address.count("\n")

        # -DE does not return address on VIES at all
        # -IE has pretty much unparsable addresses in VIES - split by commas, in different orders,
        #   without postcode codes, often without street number etc
        # -ES VIES does not return address unless you tell it what it is
        # -RO does not have postcode codes in VIES data, but we parse the rest.
        #   postcode will return false - needs to be input by customer manualy
        # -EL additionaly gets transliterated to English characters (resulting in Greeklish)

        if country_code not in self.get_vies_supported_countries():
            return None

        if (newlines == 1) and (country_code in ["NL", "BE", "FR", "FI", "AT", "PL", "DK"]):
            address_split = address.split("\n")
            street = address_split[0]
            postcode, city = address_split[1].split(" ", maxsplit=1)  # "58-500 JELENIA GÓRA"

            return {
                "street": street.strip().capitalize(),
                "postcode": postcode.strip(),
                "city": city.strip().capitalize(),
                "country_code": country_code.strip(),
            }

        if (newlines == 2) and (country_code in ["NL", "BE", "FR", "FI", "AT", "PL", "DK"]):
            """
            KOZERY
            UROCZA 54
            05-825 GRODZISK MAZOWIECKI
            """
            address_split = address.split("\n")
            street = address_split[1]
            postcode, city = address_split[2].split(" ", maxsplit=1)  # "58-500 JELENIA GÓRA"
            city = address_split[0]

            return {
                "street": street.strip().capitalize(),
                "postcode": postcode.strip(),
                "city": city.strip().capitalize(),
                "country_code": country_code.strip(),
            }

        return None
