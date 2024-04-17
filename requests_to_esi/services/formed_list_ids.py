from asgiref.sync import sync_to_async

from .base_requests import GET_request_to_esi
from .conf import action_list_type, entity_list_type
from . import errors
from dbeve_universe.models import *
from dbeve_social.models import *


@sync_to_async
def dict_to_list(db_records):
    """
    Вынос обработки результатов Models.objects.values() в отдельную функцию
    необходим, так как по этому результату нужно итерироваться внутри
    функции, помеченной как sync_to_async, а помчеать так всю объемлющую функцию 
    не хочется. Я не понимаю почему это не работает без sync_to_async, ведь
    все объемлющие функии являются асинхронными специально для этого.
    """
    internal_ids = []
    # превращаем список словарей в обычный список id
    for dict_record in db_records:
        for key in dict_record:
            internal_ids.append(dict_record[key])
    return internal_ids


@sync_to_async
def get_star_external_ids():
    """
    Вспомогательная функция для get_external_ids.
    Возвращает внешние id для Star.
    Также почему то нужно использовать sync_to_async (
    """
    external_ids = []
    systems = Systems.objects.all()
    for system in systems:
        star_id = system.response_body.get("star_id")
        if not star_id:
            print(f"System {system.system_id} has no star")
            continue
        external_ids.append(star_id)
    return external_ids

@sync_to_async
def get_corporation_external_ids():
    """
    Вспомогательная для get_external_ids.
    Формирует список всех корпораций, связанных с альянсами. Т.е.
    входящих в алли, являющихся создателем и управляющим.

    Возможно сюда можно передавать параметр battlereport, чтобы из него
    получать список корпораций, которые нужно парсить.
    """
    external_corp_id = []
    for alliance in Alliances.objects.values("response_body"):
        temp = []
        temp.extend(alliance["response_body"]["associated_corp"])
        temp.append(alliance["response_body"]["creator_corporation_id"])
        temp.append(alliance["response_body"]["executor_corporation_id"])
        temp = set(temp)
        external_corp_id.extend(temp)
    return external_corp_id


async def get_external_ids(entity:entity_list_type):
    """
    Данные можно получить либо прямым запросом к esi, либо обработкой 
    полей response_body из каких то записей в БД.
    Если существует возможность - используется прямой запрос в esi, 
    иначе - список id формируется какими то отдельными функциями.
    """
    print(f"\nStart loading all external {entity}s id.")
    if entity == "region":
        url = "https://esi.evetech.net/latest/universe/regions/?datasource=tranquility"
        external_ids = list(GET_request_to_esi(url).json())
    elif entity == "constellation":
        url = "https://esi.evetech.net/latest/universe/constellations/?datasource=tranquility"
        external_ids = list(GET_request_to_esi(url).json())
    elif entity == "system":
        url = "https://esi.evetech.net/latest/universe/systems/?datasource=tranquility"
        external_ids = list(GET_request_to_esi(url).json())
    elif entity == "star":
        external_ids = await get_star_external_ids()
    elif entity == "alliance":
        url = "https://esi.evetech.net/latest/alliances/?datasource=tranquility"
        external_ids = list(GET_request_to_esi(url).json())
    elif entity == "update_field_id_associated_corporations":
        # для сохранения списка ассоциированных корпораций нужно знать id альянсов, которым это нужно сохранять.
        db_records = Alliances.objects.values(f"alliance_id")
        external_ids = await dict_to_list(db_records)
    elif entity == "corporation":
        external_ids = await get_corporation_external_ids()
    else:
        errors.raise_entity_not_processed(entity)
    print(f"Successful loading of all {entity}s id.")
    return external_ids


async def get_internal_ids(entity:entity_list_type):
    """
    Принимает сущность, запрашивает в БД уже имеющиеся записи и возвращает их.
    """
    print(f"\nStart load internal id of {entity} model.")
    if entity == "region":
        db_records = Regions.objects.values(f"{entity}_id")
    elif entity == "constellation":
        db_records = Constellations.objects.values(f"{entity}_id")
    elif entity == "system":
        db_records = Systems.objects.values(f"{entity}_id")
    elif entity == "star":
        db_records = Stars.objects.values(f"{entity}_id)")
    elif entity == "alliance":
        db_records = Alliances.objects.values(f"{entity}_id")
    elif entity == "update_field_id_associated_corporations":
        internal_ids = []
        print(f"Set internal id of this entity {entity} in empty list - [].")
        return internal_ids
    elif entity == "corporation":
        db_records = Corporations.objects.values(f"{entity}_id")
    else:
        errors.raise_entity_not_processed(entity)
    internal_ids = await dict_to_list(db_records)
    print(f"Succesful load internal id of {entity} model.")
    return internal_ids


async def formed_list_ids_to_enter_in_DB(action:action_list_type, entity:entity_list_type):
    """
    Принимает сущность, запрашивает внутренние и внешние id для этой сущности,
    сравнивает их и возвращает те, для которых нужно выполнять запросы к esi.

    Внутренние id - те id, которые однозначно уже есть в базе.
    Внешние id - это те, по которым неизвестно, есть ли они в базе, нужно их 
    найти все, сравнить с внутренними и выяснить каких точно нет в БД.
    """
    if action == "update_all":
        print(f"\nUsed mode 'update_all'. Need load all external {entity} id.")
        external_ids = await get_external_ids(entity)
        print(f"External ids: {external_ids}.")
        return external_ids

    external_ids = await get_external_ids(entity)
    internal_ids = await get_internal_ids(entity)

    if not internal_ids:
        print(f"\nThere are no records in {entity} model. Need load all external {entity} id.")
        print(f"External ids: {external_ids}.")
        return external_ids

    print(f"\nStart compare external and internal {entity} id.")
    external_ids = set(external_ids)
    internal_ids = set(internal_ids)
    # удаляем из внешних id все те id, которые есть среди внутренних
    external_ids.difference_update(internal_ids) 
    print(f"Successful compare. Need load next id: {external_ids or 'No distinguishing ids'}")
    return list(external_ids)