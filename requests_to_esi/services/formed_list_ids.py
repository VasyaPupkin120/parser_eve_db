from asgiref.sync import sync_to_async
import json

from .base_requests import GET_request_to_esi
from .conf import action_list_type, entity_list_type
from . import errors
from dbeve_universe.models import *
from dbeve_social.models import *
from dbeve_items.models import *


@sync_to_async
def dict_to_list(db_records):
    """
    Вынос обработки результатов Models.objects.values() в отдельную функцию
    необходим, так как по этому результату нужно итерироваться внутри
    функции, помеченной как sync_to_async, а помчеать так всю объемлющую функцию 
    не хочется. Я не понимаю почему это не работает без sync_to_async, ведь
    все объемлющие функии являются асинхронными специально для этого.
    """
    temp_ids = []
    # превращаем список словарей в обычный список id
    for dict_record in db_records:
        for key in dict_record:
            temp_ids.append(dict_record[key])
    return temp_ids


@sync_to_async
def get_some_pages_external_ids(entity:entity_list_type):
    """
    Некоторых сущностей слишком много - например Groups, Types
    и список с их id нужно получать с нескольких страниц одного запроса. 
    Прчем заранее неизвестно, сколько страниц есть, поэтому 
    выполняются запросы до тех пор, пока не придет какая нибудь ошибка.
    В нормальном режиме приходит 500 ответ, если где то косяк, то GET_request_to_esi
    сгенерирует и выбросит ошибку а здесь она будет перехвачена и повторно выброшена.
    """
    # временная заглушка ,чтобы не грузить по несколько раз с esi
    # with open(f"{entity}_external_ids.json", "r") as file:
    #     external_ids = json.load(file)
    # return external_ids

    if entity == "group":
        base_url = "https://esi.evetech.net/latest/universe/groups/?datasource=tranquility&page="
    elif entity == "type":
        base_url = "https://esi.evetech.net/latest/universe/types/?datasource=tranquility&page="
    else:
        errors.raise_entity_not_processed(entity)

    page = 1
    external_ids = []
    while True:
        url = base_url + str(page)
        try:
            temp = GET_request_to_esi(url).json()
            print(f"Successful load page: {str(page)}. Load {len(temp)} ids")
            external_ids.extend(temp)
            page += 1
        except errors.StatusCodeNot200Exception as e:
            if e.full_body_response.json()["error"] == "Undefined 404 response. Original message: Requested page does not exist!":
                print(f"Succesful load all {entity} ids. Total {len(external_ids)} ids. ")
                # этот блок - на случай отладки сущностей с множестовм id - чтобы не грузить их повторно с esi
                # with open(f"{entity}_external_ids.json", "w") as file:
                #     json.dump(external_ids, file)
                # print(f"Write in file {entity}_external_ids.json")
                return external_ids
            else:
                print("\nSome unknown error.\n")
                raise e


################################################################################
#                            Блок внешних id.                                  #  
################################################################################
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
    """
    external_corp_id = []
    # id корп из инфы об альянсах
    for alliance in Alliances.objects.values("response_body"):
        temp = []
        temp.extend(alliance["response_body"]["associated_corp"])
        temp.append(alliance["response_body"]["creator_corporation_id"])
        temp.append(alliance["response_body"]["executor_corporation_id"])
        # temp = set(temp)
        external_corp_id.extend(temp)
    # id корп из истории чаров и текущей корпорации чара
    characters = Characters.objects.values("corporation_id", "response_body", "is_deleted")
    for character in characters:
        if character["is_deleted"]:
            continue
        corporation_history = character["response_body"].get("corporation_history")
        if not corporation_history:
            continue
        temp = []
        for record in corporation_history:
            temp.append(record["corporation_id"])
        if character["corporation_id"]:
            temp.append(character["corporation_id"])
        external_corp_id.extend(temp)
    return external_corp_id


@sync_to_async
def get_character_external_ids():
    """
    Вспомогательная для get_external_ids.
    Формирует список id чаров, в частности - это сео корпораций, 
    creator альянса, creator корпорации.
    """
    external_ids = []
    for alliance in Alliances.objects.values("response_body"):
        external_ids.append(alliance["response_body"]["creator_id"])
    for corporation in Corporations.objects.values("corporation_id", "response_body"):
        external_ids.append(corporation["response_body"]["creator_id"])
        ceo_id = corporation["response_body"]["ceo_id"]
        if ceo_id == 1:
            print(f"Corporation {corporation['corporation_id']} closed. Nothing CEO.")
            continue
        else:
            external_ids.append(ceo_id)
    external_ids = set(external_ids)
    # удаляем из списка загружаемых те, которые есть в БД и помечены как удаленные
    deleted_chars = Characters.objects.filter(is_deleted=True).values("character_id")
    deleted_chars_ids = []
    for deleted_char in deleted_chars:
        deleted_chars_ids.append(deleted_char["character_id"])
    deleted_chars_id = set(deleted_chars_ids)
    external_ids.difference_update(deleted_chars_id) 
    return external_ids


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
    elif entity == "load_id_associated_corporations":
        # для сохранения списка ассоциированных корпораций нужно знать id альянсов, которым это нужно сохранять.
        db_records = Alliances.objects.values("alliance_id")
        external_ids = await dict_to_list(db_records)
    elif entity == "corporation":
        external_ids = await get_corporation_external_ids()
    elif entity == "character":
        external_ids = await get_character_external_ids()
    elif entity == "load_corporation_history":
        # для сохранения списка истории корпораций у чаров нужно знать id чаров, причем тех, которые не являются удаленными
        db_records = Characters.objects.filter(is_deleted__isnull=True).values("character_id")
        external_ids = await dict_to_list(db_records)
    elif entity == "category":
        url = "https://esi.evetech.net/latest/universe/categories/?datasource=tranquility"
        external_ids = list(GET_request_to_esi(url).json())
    elif entity == "group":
        external_ids = await get_some_pages_external_ids(entity)
    elif entity == "type":
        external_ids = await get_some_pages_external_ids(entity)
    else:
        errors.raise_entity_not_processed(entity)
    print(f"Successful loading of all {entity}s id.")
    return external_ids



################################################################################
#                         Блок внутренних id.                                  #
################################################################################
@sync_to_async
def get_corporation_history_internal_ids():
    """
    Возвращаем id только тех чаров, у которых уже есть запись истории корпораций
    и эти чары не должны быть удалены.
    """
    characters = Characters.objects.filter(is_deleted__isnull=True).values("character_id", "response_body")
    internal_ids = []
    for character in characters:
        if character["response_body"].get("corporation_history"):
            internal_ids.append(character["character_id"])
    return internal_ids


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
    elif entity == "load_id_associated_corporations":
        internal_ids = []
        print(f"Set internal id of this entity {entity} in empty list - [].")
        return internal_ids
    elif entity == "corporation":
        db_records = Corporations.objects.values(f"{entity}_id")
    elif entity == "character":
        db_records = Characters.objects.values(f"{entity}_id")
    elif entity == "load_corporation_history":
        internal_ids = await get_corporation_history_internal_ids()
        return internal_ids
    elif entity == "category":
        db_records = Categories.objects.values(f"{entity}_id")
    elif entity == "group":
        db_records = Groups.objects.values(f"{entity}_id")
    elif entity == "type":
        db_records = Types.objects.values(f"{entity}_id")
    else:
        errors.raise_entity_not_processed(entity)
    # метод Models.objects.values() возвращает словарь словарей, это нужно преобразовать в список.
    internal_ids = await dict_to_list(db_records)
    print(f"Succesful load internal id of {entity} model.")
    return internal_ids


################################################################################
#                       Блок сравнения id и возврат.                           #  
################################################################################
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
