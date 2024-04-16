import aiohttp

from asgiref.sync import sync_to_async

from . import base_errors
from .base_requests import GET_request_to_esi, several_async_requests
from .enter_entitys_to_db import enter_entitys_to_db
from .asynctimer import async_timed
from .conf import NUMBER_OF_REQUEST, action_list_type, entity_list_type
from .linker_universe import *

from dbeve_universe.models import *
from dbeve_social.models import *


def create_chunks(all_id:list):
    """
    принимает большой список all_id, возвращает список разбитый на чанки - тоже списки.
    Размер чанка определяется NUMBER_OF_REQUEST.
    В последнем чанке остатки.
    """
    all_id_chunks = []
    temp = []
    for count, id_key in enumerate(all_id):
        if count % NUMBER_OF_REQUEST == 0 and count != 0:
            all_id_chunks.append(temp) 
            temp = []
        temp.append(id_key) 
    all_id_chunks.append(temp) 
    return all_id_chunks


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
    else:
        base_errors.raise_entity_not_processed(entity)
    print(f"Successful loading of all {entity}s id.")
    return external_ids


async def get_internal_ids(entity:entity_list_type):
    """
    Принимает сущность, запрашивает в БД уже имеющиеся записи и возвращает их.
    """
    @sync_to_async
    def dict_to_list(db_records):
        """
        Вынос обработки результатов Models.objects.values() в отдельную функцию
        необходим, так как по этому результату нужно итерироваться внутри
        функции, помеченной как sync_to_async, а помчеать так всю get_internal_ids 
        не хочется. Я не понимаю почему это не работает без sync_to_async, ведь
        get_internal_ids является асинхронной специально для этого.
        """
        internal_ids = []
        # превращаем список словарей в обычный список id
        for dict_record in db_records:
            for key in dict_record:
                internal_ids.append(dict_record[key])
        return internal_ids
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
    else:
        base_errors.raise_entity_not_processed(entity)
    internal_ids = await dict_to_list(db_records)
    print(f"Succesful load internal id of {entity} model.")
    return internal_ids


async def formed_list_ids_to_enter_in_DB(action:action_list_type, entity:entity_list_type):
    """
    Принимает сущность, запрашивает внутренние и внешние id для этой сущности,
    сравнивает их и возвращает те, для которых нужно выполнять запросы к esi.
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


async def linking(entity:entity_list_type):
    """
    Линковка для тех сущностей, которым она нужна.
    """
    if entity == "constellation":
        await linking_constellations()
    elif entity == "system":
        await linking_systems()
    elif entity == "star":
        await linking_stars()
    else:
        print(f"Linking for the {entity}s is not needed or the method is not defined.")



@async_timed()
async def create_all_entities(action:action_list_type, entity:entity_list_type):
    """
    Главная функция-парсер, все остальные - вспомогательные.
    Работает для случая, когда нужно спарсить сразу все записи модели.
    Определяет список id по которым нужно запросить инфу в esi,
    запрашивает инфу по этим id, вносит эту инфу в БД.
    """
    # проверка сущностей и действий
    base_errors.check_action(action)
    base_errors.check_entity(entity)

    # формирование списка id, по которым нужно обращаться в esi и запрашивать инфу
    id_for_enter_to_db = await formed_list_ids_to_enter_in_DB(action, entity)
    if not id_for_enter_to_db:
        print("\nThere are no IDs that need to be entered into the database\n")
        return

    # разбиение списка id на чанки
    chunks = create_chunks(id_for_enter_to_db)

    # старт загрузки данных с esi и сохранение в БД
    print(f"\nStart loading information about the {entity} from the ESI and saving it into the database")
    count = 0
    async with aiohttp.ClientSession() as session:
        for chunk in chunks:
            print(f"\nLoad {count * NUMBER_OF_REQUEST}/{len(id_for_enter_to_db)} {entity}s")
            data = await several_async_requests(session, chunk, entity)
            await enter_entitys_to_db(entity, data)
            count += 1
    print("Successful downloading and saving information by {entity}.")

    # запуск линковки
    await linking(entity)
