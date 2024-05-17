import json
import os
import re
import traceback
from pathlib import Path
from string import capwords
from typing import TypedDict

import requests
from loguru import logger
from pyVies import api
from RegonAPI import RegonAPI
from RegonAPI.exceptions import ApiAuthenticationError

from app.config import get_settings

settings = get_settings()


class CompanyData(TypedDict):
    name: str
    short_name: str
    street: str
    postcode: str
    city: str
    country_code: str


class CompanyInfo:
    def __init__(self, country: str, tax_id: str):
        self.country = country.upper()
        self.tax_id = re.sub(r"[^A-Za-z0-9]", "", tax_id)
        self.vat_eu = f"{self.country}{self.tax_id.upper()}"

    def get_details(self) -> CompanyData | None:
        if os.getenv("TESTING") == "1":
            logger.info("Company data test")
            return self.rejestr_io()

        try:
            for method in (self.vies, self.gus, self.rejestr_io):
                data = method()
                if data is not None:
                    return data
            return self._default_data()
        except Exception as e:
            logger.error(f"Error retrieving company details: {e}")
            traceback.print_exc()
            return None

    def vies(self):
        try:
            vies = api.Vies()
            result = vies.request(self.vat_eu, self.country, extended_info=True)
        except (api.ViesValidationError, api.ViesHTTPError, api.ViesError) as e:
            logger.error(f"Vies API error: {e}")
            return None

        if not result or not result.get("valid"):
            return None

        try:
            name = {
                "name": capwords(result["traderName"], sep=None),
                "short_name": self._get_company_short_name(result["traderName"]),
            }
            address = self._get_vies_parsed_address(result["traderAddress"])
            if address:
                return {**name, **address}
        except Exception as e:
            logger.error(f"Error parsing VIES data: {e}")
            traceback.print_exc()
        return None

    def gus(self):
        regon_api = RegonAPI(bir_version="bir1.1", is_production=False, timeout=10, operation_timeout=10)
        try:
            regon_api.authenticate(key=settings.GUS_API_DEV)
        except ApiAuthenticationError as e:
            logger.error(f"GUS API authentication error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during GUS API authentication: {e}")
            return None

        result = regon_api.searchData(nip=self.tax_id)
        if not result:
            return None

        company_name = result[0].get("Nazwa")
        if not company_name:
            return None

        company_name = self._replace_company_suffixes(company_name)

        street = " ".join(
            filter(None, [result[0].get("Ulica"), result[0].get("NrNieruchomosci"), result[0].get("NrLokalu")])
        )

        return {
            "name": company_name,
            "short_name": self._get_company_short_name(company_name),
            "street": street,
            "postcode": result[0].get("KodPocztowy", ""),
            "city": result[0].get("Miejscowosc", ""),
            "country_code": self.country,
        }

    def rejestr_io(self) -> dict | None:
        if os.getenv("TESTING") == "1":
            logger.info("Company data test")
            path = Path(__file__).parent.parent.parent.joinpath("tests", "api_responses", "rejestr_io_get_by_nip.json")
            with path.open(encoding="UTF-8") as file:
                return json.load(file)
        else:
            headers = {"Authorization": settings.REJESTR_IO_KEY}
            url = f"https://rejestr.io/api/v2/org?nip={self.tax_id}"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Rejestr.io API error: {response.status_code}")
                return None

            try:
                request_json = response.json()
                result = request_json["wyniki"][0]
                return {
                    "name": result["nazwy"]["pelna"],
                    "short_name": result["nazwy"]["pelna"],
                    "street": result["adres"]["ulica"],
                    "postcode": result["adres"]["kod"],
                    "city": result["adres"]["miejscowosc"],
                    "country_code": self.country,
                }
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing rejestr.io data: {e}")
        return None

    @staticmethod
    def _replace_company_suffixes(company_name: str) -> str:
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
        return company_name

    @staticmethod
    def _get_company_short_name(company_name: str) -> str:
        return capwords(CompanyInfo._replace_company_suffixes(company_name), sep=None)

    @staticmethod
    def get_vies_supported_countries() -> list[str]:
        return ["SK", "NL", "BE", "FR", "PT", "IT", "FI", "RO", "SI", "AT", "PL", "HR", "EL", "DK", "EE", "CZ"]

    def _get_vies_parsed_address(self, address: str) -> dict | None:
        country_code = self.country
        address_lines = address.split("\n")
        if country_code not in self.get_vies_supported_countries():
            return None

        if len(address_lines) == 2 and country_code in ["NL", "BE", "FR", "FI", "AT", "PL", "DK"]:
            street, postcode_city = address_lines
            postcode, city = postcode_city.split(" ", 1)
            return {
                "street": street.strip().capitalize(),
                "postcode": postcode.strip(),
                "city": city.strip().capitalize(),
                "country_code": country_code,
            }

        if len(address_lines) == 3 and country_code in ["NL", "BE", "FR", "FI", "AT", "PL", "DK"]:
            city, street, postcode_city = address_lines
            postcode, city = postcode_city.split(" ", 1)
            return {
                "street": street.strip().capitalize(),
                "postcode": postcode.strip(),
                "city": city.strip().capitalize(),
                "country_code": country_code,
            }

        return None

    @staticmethod
    def _default_data() -> CompanyData:
        return {
            "name": "Nie znaleziono - uzupelnij",
            "short_name": "Nie znaleziono - uzupelnij",
            "street": "",
            "postcode": "",
            "city": "",
            "country_code": "PL",
        }
