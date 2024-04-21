from asgiref.sync import sync_to_async

from .errors import raise_entity_not_processed, raise_action_not_allowed
from .base_requests import GET_request_to_esi, load_and_save_icon
from .conf import entity_list_type

from dbeve_social.models import Alliances, Characters, Corporations
from dbeve_universe.models import Constellations, Regions, Stars, Systems


###############################################################################
#                          Парсинг одной сущности.                            #
###############################################################################

def get_associated_corp(alliance_id, corp_creator_id, corp_executor_id):
    """
    Вспомогательная функция для create_or_update_one_entity()
    Получает id алли, id корпы-экзекутора, id корпы-основателя, 
    выполняет запрос, возвращает кортеж с всеми ассоциированными корпорациями.
    """
    ...
    # url = f"https://esi.evetech.net/latest/alliances/{alliance_id}/corporations/?datasource=tranquility"
    # print(f"Start load list associated corporation for alliance {alliance_id}")
    # corporations = GET_request_to_esi(url).json()
    # if corp_creator_id:
    #     corporations.append(corp_creator_id)
    # if corp_executor_id:
    #     corporations.append(corp_executor_id)
    # print(f"Successful load list associated corporation for alliance {alliance_id}")
    # # убираем дублирующиеся - creator и executor могут повторяться в общем списке корп
    # return tuple(set(corporations))


def get_corporationhistory(character_id):
    """
    Вспомогательная для create_or_update_one_entity().
    Получает id персонажа, выполняет запрос, возвращает json-ответ.
    """
    ...
    # url = f"https://esi.evetech.net/latest/characters/{character_id}/corporationhistory/?datasource=tranquility"
    # print(f"Start load corporation history for character {character_id}")
    # resp = GET_request_to_esi(url).json()
    # print(f"Successful load corporation history")
    # return resp



################################################################################
#              очень большая функция-креатор, но альтернатива -                #
#               очень много маленьких однообразных функций                     #
#     сложно придумать обобщенный вариант из-за разных имен полей в моделях    #
################################################################################


# пришлось преобразовать enter_entitys_to_db в асинхронную, т.к. иначе запись в БД
# вызывала ошибку django.core.exceptions.SynchronousOnlyOperation
# соответсвенно, ее нужно вызывать через await
@sync_to_async
def enter_entitys_to_db(
        entity: entity_list_type,
        data:dict,
        ):
    """
    Исключительно для сохранения данных в БД. Получает словарь и сохраняет данные из него в БД.

    Функция получает тип сущности и словарь с данными и вносит данные по 
    значению в БД. Количество записей в словаре зависит от размера чанка.
    data - словарь, полученный из функции several_async_requests

    Не выполняет связывание записей - линковка выполняется отдельной функцией.
    В том числе для альянсов не выполняется подгрузка ассоциированных корпораций - 
    это делать отдельно, в функции внешних id для корпораций.

    в начале идут блоки для обработки universe-данных, потом блоки social-данных

    Функция не занимается загрузкой и сохранением изображений. Это нужно как-то
    отдельно делать.
    """

    # LSP ругается, но все работает. Эта проверка нужна, 
    # чтобы не выполнять впустую запросы для ошибочных параметров
    if entity not in entity_list_type.__args__:
        raise_entity_not_processed(entity)

    # запись данных по региону
    if entity == "region":
        for key in data:
            Regions.objects.update_or_create(
                    region_id=key,
                    defaults={
                        "region_id": key,
                        "name": data[key].get("name"),
                        "description": data[key].get("description"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")

    # запись данных по констелляции
    elif entity == "constellation":
        for key in data:
            Constellations.objects.update_or_create(
                    constellation_id=key,
                    defaults={
                        "constellation_id": key,
                        "name": data[key].get("name"),
                        "position_x": data[key].get("position")["x"],
                        "position_y": data[key].get("position")["y"],
                        "position_z": data[key].get("position")["z"],
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")

    # запись данных по системе
    elif entity == "system":
        for key in data:
            Systems.objects.update_or_create(
                    system_id=key,
                    defaults={
                        "name": data[key].get("name"),
                        "position_x": data[key].get("position")["x"],
                        "position_y": data[key].get("position")["y"],
                        "position_z": data[key].get("position")["z"],
                        "security_class": data[key].get("security_class"),
                        "security_status": data[key].get("security_status"),
                        "system_id": key,
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")

    # запись данных по звезде
    elif entity == "star":
        for key in data:
            Stars.objects.update_or_create(
                    star_id=key,
                    defaults={
                        "age": data[key].get("age"),
                        "luminosity": data[key].get("luminosity"),
                        "name": data[key].get("name"),
                        "radius": data[key].get("radius"),
                        "spectral_class": data[key].get("spectral_class"),
                        "star_id": key,
                        "temperature": data[key].get("temperature"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")

    # запись данных по альянсу
    elif entity == "alliance":
        for key in data:
            Alliances.objects.update_or_create(
                    alliance_id=key,
                    defaults={
                        "alliance_id": key,
                        "date_founded": data[key].get("date_founded"),
                        "name": data[key].get("name"),
                        "ticker": data[key].get("ticker"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")

    # запись списка id корпораций в поле response_body для альянса.
    elif entity == "update_field_id_associated_corporations":
        for key in data:
            alliance = Alliances.objects.get(alliance_id = key)
            alliance.response_body["associated_corp"] = data[key]
            alliance.save()
            print(f"Successful save list associated corp in alliance: {key}\n")

    # запись данных по корпорации
    elif entity == "corporation":
        for key in data:
            Corporations.objects.update_or_create(
                    corporation_id=key,
                    defaults={
                        "corporation_id": key,
                        "date_founded": data[key].get("date_founded"),
                        "description": data[key].get("description"),
                        "member_count": data[key].get("member_count"),
                        "name": data[key].get("name"),
                        "shares": data[key].get("shares"),
                        "ticker": data[key].get("ticker"),
                        "tax_rate": data[key].get("tax_rate"),
                        "url": data[key].get("url"),
                        "war_eligible": data[key].get("war_eligible"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")

    # запись данных по корпорации
    elif entity == "character":
        for key in data:
            Characters.objects.update_or_create(
                    character_id=key,
                    defaults={
                        "character_id": key,
                        "birthday": data[key].get("birthday"),
                        "description": data[key].get("description"),
                        "is_deleted": data[key].get("is_deleted"),
                        "gender": data[key].get("gender"),
                        "name": data[key].get("name"),
                        "security_status": data[key].get("security_status"),
                        "title": data[key].get("title"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
    else:
        raise_entity_not_processed(entity)

    # # парсер отдельного персонажа
    # if entity == "character":
    #     if action == "create":
    #         try:
    #             Characters.objects.get(character_id=entity_id)
    #             print(f"Character {entity_id} already exists in DB")
    #             return
    #         except ObjectDoesNotExist:
    #             print(f"Start load character: {entity_id}")
    #     url = f"https://esi.evetech.net/latest/characters/{entity_id}/?datasource=tranquility"
    #     resp = GET_request_to_esi(url).json()
    #     # изображение пока не грузить, не особо нужно
    #     # nameicon = load_and_save_icon(entity, entity_id)
    #     corporation_history = get_corporationhistory(entity_id)
    #     resp["corporation_history"] = corporation_history
    #     print(f"Successful load character: {entity_id}")
    #     Characters.objects.update_or_create(
    #             character_id=entity_id,
    #             defaults={
    #                 "character_id": entity_id,
    #                 "birthday": resp.get("birthday"),
    #                 "description": resp.get("description"),
    #                 "gender": resp.get("gender"),
    #                 "name": resp.get("name"),
    #                 # "nameicon": nameicon,
    #                 "security_status": resp.get("security_status"),
    #                 "title": resp.get("title"),
    #                 "response_body": resp,
    #                 }
    #             )
    #     print(f"Successful save to DB character: {entity_id}")
