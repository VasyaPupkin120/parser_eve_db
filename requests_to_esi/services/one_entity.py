from typing import Literal

from django.core.exceptions import ObjectDoesNotExist

from dbeve_universe.models import Constellations, Regions, Stars, Systems

from .base_requests import GET_request_to_esi, load_and_save_icon, entity_not_processed, action_not_allowed
from dbeve_social.models import Alliances


###############################################################################
#                          Парсинг одной сущности.                            #
###############################################################################

entity_list_type = Literal["region", "constellation", "system", "star", "alliance", "corporation", "character"] 
action_list_type = Literal["create", "update"]

def create_or_update_one_entity(
        entity: entity_list_type,
        entity_id, 
        action: action_list_type,
        **kwargs,
        ):
    """
    Функция для первоначальной загрузки или для обновления информации
    об одной сущности.

    Режим update - это однозначно загрузить данные с esi и обновить запись. Нужно
    когда БД уже сформирована и требуется собственно обновить одну запись.

    Режим create - это проверить, есть ли такая запись в БД и если есть, 
    то не запрашивать данные с esi. Нужно для первоначального заполнения БД - 
    когда парсинг приходится запускать по несколько раз.

    соответственно, более нет необходимости в множестве функций-парсеров отдельных алли, систем и т.д.
    все это можно делать через текущую функцию.

    в начале идут блоки для обработки universe-данных, потом блоки social-данных
    """

    # LSP ругается, но все работает. Эта проверка нужна, 
    # чтобы не выполнять впустую запросы для ошибочных параметров
    if entity not in entity_list_type.__args__:
        entity_not_processed(entity)
    if action not in action_list_type.__args__:
        action_not_allowed(action)
    
    # парсер региона
    if entity == "region":
        # если не хочется сначала обращаться в esi а потом сравнивать поля. 
        # этот шаг пропускается для случая, когда нужно обновить запись - 
        # так как для обновления нужно и сходить в esi и сравнить поля
        if action == "create":
            try:
                Regions.objects.get(region_id=entity_id)
                print(f"Region {entity_id} already exists in DB")
                return
            except ObjectDoesNotExist:
                print(f"Start load region: {entity_id}")
        url = f"https://esi.evetech.net/latest/universe/regions/{entity}/?datasource=tranquility&language=en"
        resp = GET_request_to_esi(url).json()
        print(f"Successful load region: {resp['region_id']}")
        Regions.objects.update_or_create(
                region_id=resp["region_id"],
                defaults={
                    "region_id": resp["region_id"],
                    "name": resp.get("name"),
                    "description": resp.get("description"),
                    "response_body": resp, 
                    }
                )
        print(f"Successful save to DB region: {resp['region_id']}\n")

    # парсер констелляции
    if entity == "constellation":
        if action == "create":
            try:
                Constellations.objects.get(constellation_id=entity_id)
                print(f"Constellation {entity_id} already exists in DB")
                return
            except ObjectDoesNotExist:
                print(f"Start load constellation: {entity_id}")
        url = f"https://esi.evetech.net/latest/universe/constellations/{entity_id}/?datasource=tranquility&language=en"
        resp = GET_request_to_esi(url).json()
        print(f"Successful load constellation: {resp['constellation_id']}")
        region = Regions.objects.get(region_id=resp["region_id"])
        Constellations.objects.update_or_create(
                constellation_id=resp["constellation_id"],
                defaults={
                    "constellation_id": resp["constellation_id"],
                    "name": resp.get("name"),
                    "position_x": resp.get("position")["x"],
                    "position_y": resp.get("position")["y"],
                    "position_z": resp.get("position")["z"],
                    "region": region,
                    "response_body": resp,
                    }
                )
        print(f"Successful save to DB constellation: {resp['constellation_id']}")

    # парсер системы
    if entity == "system":
        if action == "create":
            try:
                Systems.objects.get(system_id=entity_id)
                print(f"System {entity_id} already exists in DB")
                return
            except ObjectDoesNotExist:
                print(f"Start load system: {entity_id}")
        url = f"https://esi.evetech.net/latest/universe/systems/{entity_id}/?datasource=tranquility&language=en"
        resp = GET_request_to_esi(url).json()
        print(f"Successful load system: {resp['system_id']}")
        constellation = Constellations.objects.get(constellation_id=resp["constellation_id"])
        Systems.objects.update_or_create(
                system_id=resp["system_id"],
                defaults={
                    "constellation": constellation,
                    "name": resp.get("name"),
                    "position_x": resp.get("position")["x"],
                    "position_y": resp.get("position")["y"],
                    "position_z": resp.get("position")["z"],
                    "security_class": resp.get("security_class"),
                    "security_status": resp.get("security_status"),
                    "system_id": resp["system_id"],
                    "response_body": resp,
                    }
                )
        print(f"Successful save to DB system: {resp['system_id']}")

    # парсер звезды
    # должен через аргумент функции kwargs["solar_system"] получать ссылку на звезду, с которой будет связан
    if entity == "star":
        if action == "create":
            try:
                Stars.objects.get(star_id=entity_id)
                print(f"Star {entity_id} already exists in DB")
                return
            except ObjectDoesNotExist:
                print(f"Start load star: {entity_id}")
        url = f"https://esi.evetech.net/latest/universe/stars/{entity_id}/?datasource=tranquility"
        resp = GET_request_to_esi(url).json()
        print(f"Successful load star: {entity_id}")
        Stars.objects.update_or_create(star_id=entity_id,
                                       defaults={
                                           "age": resp.get("age"),
                                           "luminosity": resp.get("luminosity"),
                                           "name": resp.get("name"),
                                           "radius": resp.get("radius"),
                                           "solar_system": kwargs["solar_system"],
                                           "spectral_class": resp.get("spectral_class"),
                                           "star_id": entity_id,
                                           "temperature": resp.get("temperature"),
                                           "response_body": resp,
                                           }
                                       )
        print(f"Successful save to DB star: {entity_id}")

    # парсер альянса
    if entity == "alliance":
        if action == "create":
            try:
                Alliances.objects.get(alliance_id=entity_id)
                print(f"Alliance {entity_id} already exists in DB")
                return
            except ObjectDoesNotExist:
                print(f"Start load alliance: {entity_id}")
        url = f"https://esi.evetech.net/latest/alliances/{entity_id}/?datasource=tranquility"
        resp = GET_request_to_esi(url).json()
        nameicon = load_and_save_icon(entity, entity_id)
        print(f"Successful load alliance: {entity_id}")
        Alliances.objects.update_or_create(
                alliance_id=entity_id,
                defaults={
                    "alliance_id": entity_id,
                    "date_founded": resp.get("date_founded"),
                    "name": resp.get("name"),
                    "ticker": resp.get("ticker"),
                    "response_body": resp,
                    "nameicon": nameicon,
                    }
                )
        print(f"Successful save to DB alliance: {entity_id}")

            
