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


arr = []
sub_arr = []


def extract_path_from_json(obj: dict | list, sub_arr: list, val: str) -> list[list]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            found_arr = [*sub_arr, k]
            if isinstance(v, (dict, list)):
                extract_path_from_json(v, found_arr, val)
            elif v == val:
                arr.append(found_arr)
    elif isinstance(obj, list):
        for item in obj:
            found_arr = [*sub_arr, obj.index(item)]
            if isinstance(item, (dict, list)):
                extract_path_from_json(item, found_arr, val)
            elif item == val:
                arr.append(found_arr)
    return arr


def traverse_dict_by_path(dictionary: dict, path: list):
    for item in path:
        dictionary = dictionary[item]
    return dictionary


def get_mentions_uuids(json_object: dict, keyword: str) -> list:
    mention_uuids = []
    mentions_paths = []
    arr = []
    sub_arr = []
    mentions_paths = extract_path_from_json(json_object, [], keyword)

    print(keyword)
    print(mentions_paths)

    if mentions_paths:
        for path in mentions_paths:
            mention = traverse_dict_by_path(json_object, path[:-1])  #
            mention_uuids.append(mention["attrs"]["id"])

    return mention_uuids
