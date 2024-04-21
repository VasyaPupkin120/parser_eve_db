import aiohttp

from asgiref.sync import sync_to_async

from . import errors
from .base_requests import several_async_requests
from .enter_entitys_to_db import enter_entitys_to_db
from .asynctimer import async_timed
from .conf import NUMBER_OF_REQUEST, action_list_type, entity_list_type
from .linker import *
from .formed_list_ids import formed_list_ids_to_enter_in_DB

from dbeve_universe.models import *
from dbeve_social.models import *


def create_chunks(ids:list):
    """
    принимает большой список ids, возвращает список разбитый на чанки - тоже списки.
    Размер чанка определяется NUMBER_OF_REQUEST.
    В последнем чанке остатки.
    """
    ids_chunks = []
    temp = []
    for count, id_key in enumerate(ids):
        if count % NUMBER_OF_REQUEST == 0 and count != 0:
            ids_chunks.append(temp) 
            temp = []
        temp.append(id_key) 
    ids_chunks.append(temp) 
    return ids_chunks



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
    elif entity == "corporation":
        await linking_corporations()
    else:
        print(f"Linking for the {entity}s is not needed or the method is not defined.")



@async_timed()
async def create_all_entities(action:action_list_type, entity:entity_list_type, list_of_entities:list|None=None):
    """
    Главная функция-парсер, все остальные - вспомогательные или независмые.

    Определяет список id по которым нужно запросить инфу в esi,
    запрашивает инфу по этим id из esi, вносит эту инфу в БД.

    Если нужно внести данные не по целой модели а дополнить поле модели, эта функция
    тоже пригодна, просто нужно задать сущность для этого действия и для этой сущности
    определить нужные действия в функции enter_entitys_to_db() - т.е. не сохранять 
    все поля, а обновить только одно. Внутренние id для этой цели можно 
    выставлять пустыми - [] в функции управляющей выделением внутренних id.

    если нужно выполнить парсинг не всех сущностей, а только ограниченного набора,
    то набор их id можно передать в list_of_entites - он будет считаться внешними
    id.
    """
    # проверка сущностей и действий
    errors.check_action(action)
    errors.check_entity(entity)

    # формирование списка id, по которым нужно обращаться в esi и запрашивать инфу
    if list_of_entities:
        id_for_enter_to_db = list_of_entities
    else:
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


