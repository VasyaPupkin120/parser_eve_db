from typing import Literal

from django.core.exceptions import ObjectDoesNotExist
from .base_requests import GET_request_to_esi
from dbeve_social.models import Alliances

from .one_entity import create_or_update_one_entity


def create_or_update_all_alliances(action: Literal["update", "create"]):
    url = "https://esi.evetech.net/latest/alliances/?datasource=tranquility"
    alliances_id = GET_request_to_esi(url).json()
    len_alliances = len(alliances_id)
    count = 1
    print("\nSuccessful loading of all alliances id.")
    print("Start downloading information by alliance.")
    for alliance_id in alliances_id:
        print(f"\nLoad: {count}/{len_alliances}")
        create_or_update_one_entity("alliance", alliance_id, action)
        count += 1
