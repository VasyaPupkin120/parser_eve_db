from asgiref.sync import sync_to_async

from .base_errors import raise_entity_not_processed, raise_action_not_allowed
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
    # FIXME перенести связывание Stars, Systems, Constellations в отдельную функцию-линкер
    # здесь должен быть исключительно парсинг, без линковки
    """
    Получает словарь и сохраняет данные из него в БД.

    Функция получает тип сущности и словарь с данными и 
    вносит данные по значению в БД. Количество записей в словаре зависит от размера чанка
    data - словарь, полученный из функции several_async_requests, последний раз
    эта функция передавала только тело ответа без заголовков.

    ЛИНКОВКА СВЯЗЕЙ ТАКЖЕ ДОЛЖНА ОСУЩЕСТВЛЯТЬСЯ ДРУГОЙ ФУНКЦИЕЙ.
    ВСЕ ПОЛЯ ВНЕШНЕГО КЛЮЧА НЕ ДОЛЖНЫ ЗАПОЛНЯТЬСЯ ЗДЕСЬ!!
    ЛИНКОВКА - ПОТОМ, НА ОСНОВЕ ПОЛЯ response_body, В КОТОРОМ ЕСТЬ ИНФА ПО СВЯЗЯМ.

    Нет разделения на create и update - функция однозначно вносит все полученные данные в БД.

    соответственно, более нет необходимости в множестве функций-парсеров 
    отдельных алли, систем и т.д. все это можно делать через текущую функцию.

    в начале идут блоки для обработки universe-данных, потом блоки social-данных

    #FIXME после написаниия линкера для Systems убрать эти аргументы
    возможные варианты аргументов, полученные через kwargs:
        solar_system - солнечная система для Stars
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
            print(f"Successful save to DB region: {key}\n")

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
            print(f"Successful save to DB constellation: {key}\n")

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
            print(f"Successful save to DB system: {key}\n")
    else:
        raise_entity_not_processed(entity)

    #
    # # парсер звезды
    # # должен через аргумент функции kwargs["solar_system"] получать ссылку на звезду, с которой будет связан
    # if entity == "star":
    #     if action == "create":
    #         try:
    #             Stars.objects.get(star_id=entity_id)
    #             print(f"Star {entity_id} already exists in DB")
    #             return
    #         except ObjectDoesNotExist:
    #             print(f"Start load star: {entity_id}")
    #     url = f"https://esi.evetech.net/latest/universe/stars/{entity_id}/?datasource=tranquility"
    #     resp = GET_request_to_esi(url).json()
    #     print(f"Successful load star: {entity_id}")
    #     Stars.objects.update_or_create(star_id=entity_id,
    #                                    defaults={
    #                                        "age": resp.get("age"),
    #                                        "luminosity": resp.get("luminosity"),
    #                                        "name": resp.get("name"),
    #                                        "radius": resp.get("radius"),
    #                                        "solar_system": kwargs["solar_system"],
    #                                        "spectral_class": resp.get("spectral_class"),
    #                                        "star_id": entity_id,
    #                                        "temperature": resp.get("temperature"),
    #                                        "response_body": resp,
    #                                        }
    #                                    )
    #     print(f"Successful save to DB star: {entity_id}")
    #
    # # парсер альянса
    # if entity == "alliance":
    #     if action == "create":
    #         try:
    #             Alliances.objects.get(alliance_id=entity_id)
    #             print(f"Alliance {entity_id} already exists in DB")
    #             return
    #         except ObjectDoesNotExist:
    #             print(f"Start load alliance: {entity_id}")
    #     url = f"https://esi.evetech.net/latest/alliances/{entity_id}/?datasource=tranquility"
    #     resp = GET_request_to_esi(url).json()
    #     associated_corp = get_associated_corp(entity_id, resp.get("creator_corporation_id"), resp.get("executor_corporation_id"))
    #     # вносим корпорации в response_body, в котором этой инфы не было - чтобы не создавать дополнительные поля модели
    #     resp["associated_corp"] = associated_corp
    #     nameicon = load_and_save_icon(entity, entity_id)
    #     print(f"Successful load alliance: {entity_id}")
    #     Alliances.objects.update_or_create(
    #             alliance_id=entity_id,
    #             defaults={
    #                 "alliance_id": entity_id,
    #                 "date_founded": resp.get("date_founded"),
    #                 "name": resp.get("name"),
    #                 "ticker": resp.get("ticker"),
    #                 "response_body": resp,
    #                 "nameicon": nameicon,
    #                 }
    #             )
    #     print(f"Successful save to DB alliance: {entity_id}")
    #
    # # парсер корпорации
    # if entity == "corporation":
    #     if action == "create":
    #         try:
    #             Corporations.objects.get(corporation_id=entity_id)
    #             print(f"Corporation {entity_id} already exists in DB")
    #             return
    #         except ObjectDoesNotExist:
    #             print(f"Start load corporation: {entity_id}")
    #     url = f"https://esi.evetech.net/latest/corporations/{entity_id}/?datasource=tranquility"
    #     resp = GET_request_to_esi(url).json()
    #     nameicon = load_and_save_icon(entity, entity_id)
    #     print(f"Successful load corporation: {entity_id}")
    #     Corporations.objects.update_or_create(
    #             corporation_id=entity_id,
    #             defaults={
    #                 "corporation_id": entity_id,
    #                 "date_founded": resp.get("date_founded"),
    #                 "description": resp.get("description"),
    #                 "member_count": resp.get("member_count"),
    #                 "name": resp.get("name"),
    #                 "nameicon": nameicon,
    #                 "shares": resp.get("shares"),
    #                 "ticker": resp.get("ticker"),
    #                 "tax_rate": resp.get("tax_rate"),
    #                 "url": resp.get("url"),
    #                 "war_eligible": resp.get("war_eligible"),
    #                 "response_body": resp,
    #                 }
    #             )
    #     print(f"Successful save to DB corporation: {entity_id}")
    #
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
