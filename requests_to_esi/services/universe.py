import asyncio
from typing import Literal
from django.core.exceptions import ObjectDoesNotExist
from base_requests import GET_request_to_esi 
from async_base_requests import several_async_requests
# from one_entity import enter_one_entity_to_DB
# from dbeve_universe.models import Regions, Constellations
# from dbeve_universe.models import *
import json
import aiohttp


# создать универсальную функцию загрузки объекта сложно - нужно как то выделить список полей которые вносить в модеь
# все подряд поля ответа вносить не получится - часть этих полей это ссылки на другие модели, которых еще нет

# выглядит как чрезмерное дублирование кода, но хз как это обойти - слишком много возни с разными полями.

# регионы, констелляции - их не так много, поэтому они в любом случае загружаются с esi и выполняется update_or_create
# систем много, поэтому нужно точно знать, нужен ли запрос в esi для получения новой информации и обновления данных в БД
# звезды вроде как не должны изменяться, поэтому оставил как есть. При необходимости можно также разделить случаи или снова отпарсить все звезды

# общее количество конкурентных запросов.
NUMBER_OF_REQUEST = 20


def create_chunks(all_id):
    """
    принимает большой список данных, возвращает список разбитый на чанки.
    Размер чанка определяется NUMBER_OF_REQUEST.
    В последнем чанке остатки.
    """
    all_id = all_id[:]
    all_id_chunks = []
    temp = []
    for count, id_key in enumerate(all_id):
        if count % NUMBER_OF_REQUEST == 0 and count != 0:
            all_id_chunks.append(temp[:]) 
            temp = []
        temp.append(id_key) 
    all_id_chunks.append(temp[:]) 
    return all_id_chunks


async def create_all_regions():
    """
    Получает список регионов, чанками асинхронно запрашивает данные у esi,
    сохраняет данные в БД c помощью create_or_update_one_entity
    """
    url_get_ids_all_regions = "https://esi.evetech.net/latest/universe/regions/?datasource=tranquility"
    all_id = GET_request_to_esi(url_get_ids_all_regions).json()
    all_id = list(all_id)
    count = 1
    print("\nSuccessful loading of all region id.")
    print("Start downloading information by region.")
    chunks = create_chunks(all_id)
    base_url = "https://esi.evetech.net/latest/universe/regions/!/?datasource=tranquility&language=en"


    async with aiohttp.ClientSession() as session:
        for chunk in chunks[:2]:
            data = await several_async_requests(session, base_url, chunk)
            print(data)
            # print(f"\nLoad: {count}/{len(all_id)}")
            # create_or_update_one_entity("region", region_id, "create")
            # count += 1


# def create_all_constellations():
#     """
#     Запрашивает и обрабатывает весь список констелляций.
#     """
#     url = "https://esi.evetech.net/latest/universe/constellations/?datasource=tranquility"
#     all_id = GET_request_to_esi(url).json()
#     all_id = list(all_id)
#     count = 1
#     print("\nSuccessful loading of all constellation id.")
#     print("Start downloading information by constellation.")
#     for constellation_id in all_id:
#         print(f"\nLoad: {count}/{len(all_id)}")
#         create_or_update_one_entity("constellation", constellation_id, "create")
#         count += 1
#
#
# def create_all_systems():
#     """
#     Запрашивает у esi список систем, обрабатывает их.
#     """
#     url = "https://esi.evetech.net/latest/universe/systems/?datasource=tranquility"
#     all_id = GET_request_to_esi(url).json()
#     all_id = list(all_id)
#     count = 1
#     print("\nSuccessful loading of all system id.")
#     print("Start downloading information by system.")
#     for system_id in all_id:
#         print(f"\nLoad: {count}/{len(all_id)}")
#         create_or_update_one_entity("system", system_id, "create")
#         count += 1
#
#
# def create_all_stars():
#     """
#     Загружает из БД список систем, находит в response_body системы id звезды,
#     выполняет запрос, создает запись звезды.
#
#     причем что интересно, в теле ответа звезды нет информации об самой себе - об star_id
#     Приходится брать star_id из информации об системе
#     """
#     count = 1
#     systems = Systems.objects.all()
#     amount_systems = len(systems)
#     print("Start downloading information by stars.")
#     for system in systems:
#         print(f"\nLoad: {count}/{amount_systems}")
#         star_id = system.response_body.get("star_id")
#         if not star_id:
#             print(f"System {system.system_id} has no star")
#             count += 1 
#             continue
#         create_or_update_one_entity(entity="star", entity_id=star_id, action="create", solar_system=system)
#         count += 1 

if __name__ == "__main__":
#     list_id = [
# 10000001, 10000002, 10000003, 10000004, 10000005, 10000006, 10000007, 10000008, 10000009, 10000010, 10000011, 10000012, 10000013, 10000014, 10000015, 10000016, 10000017, 10000018, 10000019, 10000020, 10000021, 10000022, 10000023, 10000025, 10000027, 10000028, 10000029, 10000030, 10000031, 10000032, 10000033, 10000034, 10000035, 10000036, 10000037, 10000038, 10000039, 10000040, 10000041, 10000042, 10000043, 10000044, 10000045, 10000046, 10000047, 10000048, 10000049, 10000050, 10000051, 10000052, 10000053, 10000054, 10000055, 10000056, 10000057, 10000058, 10000059, 10000060, 10000061, 10000062, 10000063, 10000064, 10000065, 10000066, 10000067, 10000068, 10000069, 10000070, 10001000, 11000001, 11000002, 11000003, 11000004, 11000005, 11000006, 11000007, 11000008, 11000009, 11000010, 11000011, 11000012, 11000013, 11000014, 11000015, 11000016, 11000017, 11000018, 11000019, 11000020, 11000021, 11000022, 11000023, 11000024, 11000025, 11000026, 11000027, 11000028, 11000029, 11000030, 11000031, 11000032, 11000033, 12000001, 12000002, 12000003, 12000004, 12000005, 14000001, 14000002, 14000003, 14000004, 14000005
#         ]
#     create_chunks(list_id)
    asyncio.run(create_all_regions())

