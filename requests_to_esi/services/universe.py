from typing import Literal
from django.core.exceptions import ObjectDoesNotExist
from .base_requests import GET_request_to_esi 
from .one_entity import create_or_update_one_entity
from dbeve_universe.models import Regions, Constellations
from dbeve_universe.models import *
import json


# создать универсальную функцию загрузки объекта сложно - нужно как то выделить список полей которые вносить в модеь
# все подряд поля ответа вносить не получится - часть этих полей это ссылки на другие модели, которых еще нет

# выглядит как чрезмерное дублирование кода, но хз как это обойти - слишком много возни с разными полями.

# регионы, констелляции - их не так много, поэтому они в любом случае загружаются с esi и выполняется update_or_create
# систем много, поэтому нужно точно знать, нужен ли запрос в esi для получения новой информации и обновления данных в БД
# звезды вроде как не должны изменяться, поэтому оставил как есть. При необходимости можно также разделить случаи или снова отпарсить все звезды


def create_all_regions():
    """
    Получение и обработка списка регионов.
    """
    url = "https://esi.evetech.net/latest/universe/regions/?datasource=tranquility"
    all_id = GET_request_to_esi(url).json()
    all_id = list(all_id)
    count = 1
    print("\nSuccessful loading of all region id.")
    print("Start downloading information by region.")
    for region_id in all_id:
        print(f"\nLoad: {count}/{len(all_id)}")
        create_or_update_one_entity("region", region_id, "create")
        count += 1


def create_all_constellations():
    """
    Запрашивает и обрабатывает весь список констелляций.
    """
    url = "https://esi.evetech.net/latest/universe/constellations/?datasource=tranquility"
    all_id = GET_request_to_esi(url).json()
    all_id = list(all_id)
    count = 1
    print("\nSuccessful loading of all constellation id.")
    print("Start downloading information by constellation.")
    for constellation_id in all_id:
        print(f"\nLoad: {count}/{len(all_id)}")
        create_or_update_one_entity("constellation", constellation_id, "create")
        count += 1


def create_all_systems():
    """
    Запрашивает у esi список систем, обрабатывает их.
    """
    url = "https://esi.evetech.net/latest/universe/systems/?datasource=tranquility"
    all_id = GET_request_to_esi(url).json()
    all_id = list(all_id)
    count = 1
    print("\nSuccessful loading of all system id.")
    print("Start downloading information by system.")
    for system_id in all_id:
        print(f"\nLoad: {count}/{len(all_id)}")
        create_or_update_one_entity("system", system_id, "create")
        count += 1


def create_all_stars():
    """
    Загружает из БД список систем, находит в response_body системы id звезды,
    выполняет запрос, создает запись звезды.

    причем что интересно, в теле ответа звезды нет информации об самой себе - об star_id
    Приходится брать star_id из информации об системе
    """
    count = 1
    systems = Systems.objects.all()
    amount_systems = len(systems)
    print("Start downloading information by stars.")
    for system in systems:
        print(f"\nLoad: {count}/{amount_systems}")
        star_id = system.response_body.get("star_id")
        if not star_id:
            print(f"System {system.system_id} has no star")
            count += 1 
            continue
        create_or_update_one_entity(entity="star", entity_id=star_id, action="create", solar_system=system)
        count += 1 
