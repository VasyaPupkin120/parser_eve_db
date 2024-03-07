from django.core.exceptions import ObjectDoesNotExist
from .base_requests import GET_request_to_esi
from dbeve_universe.models import Regions, Constellations
from dbeve_universe.models import *
import json





def get_and_save_all_regions(action="update"):
    """
    Запрашиваем список id регионов, сравниваем с имеющимся списком id регионов в БД,
    если есть новые регионы - добавляем id этого региона в БД. 
        https://esi.evetech.net/latest/universe/regions/?datasource=tranquility

    После чего для  каждого id региона из БД, выполняем функцию для одного региона get_and_save_one_region()
    в который передаем id этого региона
    """
    url = "https://esi.evetech.net/latest/universe/regions/?datasource=tranquility"
    all_id = GET_request_to_esi(url).json()
    all_id = list(all_id)
    for region_id in all_id:
        if action == "create":
            create_one_region(region_id)
        else:
            update_one_region(region_id)

def create_one_region(region_id):
    """
    получает id региона, проверяет не полные ли данные по региону и если не полные - то
    выполняет запрос по этому id и сохраняет в БД. Если полные, то ничего не делает
    """
    url = f"https://esi.evetech.net/latest/universe/regions/{region_id}/?datasource=tranquility&language=en"
    try:
        region = Regions.objects.get(region_id=region_id)
    except ObjectDoesNotExist:
        resp = GET_request_to_esi(url).json()
        Regions.objects.create(
                region_id=resp["region_id"],
                name=resp.get("name"),
                description=resp.get("description"),
                response_body=resp,
                )

def update_one_region(region_id):
    """
    Обновляет все данные региона
    """
    url = f"https://esi.evetech.net/latest/universe/regions/{region_id}/?datasource=tranquility&language=en"
    resp = GET_request_to_esi(url).json()
    Regions.objects.update_or_create(
            region_id=resp["region_id"],
            defaults={
                "name": resp.get("name"),
                "description": resp.get("description"),
                "response_body": resp, 
                }
            )


def get_and_save_all_constellations(action="update"):
    """
    Функция запрашивает список id констеллций  - сразу всех 
    проходим по списку констелляций и отправляем каждую по очереди в get_and_save_one_constellations
    """
    url = "https://esi.evetech.net/latest/universe/constellations/?datasource=tranquility"
    all_id = GET_request_to_esi(url).json()
    all_id = list(all_id)
    for constellation_id in all_id:
        if action == 'create':
            create_one_constellation(constellation_id)
        else:
            update_one_constellation(constellation_id)


def create_one_constellation(constellation_id):
    """
    выполняем запрос инфы по констелляции, получаем всю инфу по ней
    """
    url = f"https://esi.evetech.net/latest/universe/constellations/{constellation_id}/?datasource=tranquility&language=en"
    try:
        constellation = Constellations.objects.get(constellation_id=constellation_id)
        print("try")
    except ObjectDoesNotExist:
        resp = GET_request_to_esi(url).json()
        region = Regions.objects.get(region_id=resp["region_id"])
        print(resp, "\n", region)
        constellation = Constellations.objects.create(
                constellation_id=resp["constellation_id"],
                name=resp.get("name"),
                position_x=resp.get("position")["x"],
                position_y=resp.get("position")["y"],
                position_z=resp.get("position")["z"],
                region=region,
                response_body=resp,
                )
        print(constellation)

def update_one_constellation(constellation_id):
    """
    обновление информации по констелляциям
    """
    url = f"https://esi.evetech.net/latest/universe/constellations/{constellation_id}/?datasource=tranquility&language=en"
    resp = GET_request_to_esi(url).json()
    region = Regions.objects.get(region_id=resp["region_id"])
    constellation = Constellations.objects.update_or_create(
            constellation_id=resp["constellation_id"],
            defaults={
                "name": resp.get("name"),
                "position_x": resp.get("position")["x"],
                "position_y": resp.get("position")["y"],
                "position_z": resp.get("position")["z"],
                "region": region,
                "response_body": resp,
                }
            )




def get_and_save_systems(list_systems:list):
    """
    функция рассчитана на получение небольшого списка id систем из get_and_save_one_constellations,
    но также можно передать список вообще всех систем, полученный специальным запросом.

    для каждого id из списка проверяем  наличие в БД и если нет - то создаем такую запись.

    после чего для каждого id системы выполняем запрос функции get_and_save_one_system
    """
    list_systems = list_systems[:]
    ...

def get_and_save_one_system(system_id):
    """
    Предполагается что запись об системе с данным id уже есть в БД но 
    неизвестно, есть ли другие данные в этой записи. 

    То есть, нужно определить, полны ли данные об системе, и если это только id,
    то выполняется запрос к esi, иначе запрос не должен выполняться. 

    если в ответе есть группы или типы, то перед занесением инфы в БД по системе 
    нужно создать группу и тип и привязать тип к группе. Полностью парсить все типы 
    не нужно
    """
    # system = Systems.objects.get(id=system_id)
    #
    # if system.name:
    #     return "this system has full data"
    #
    # url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/?datasource=tranquility&language=en"
    # resp = GET_request_to_esi(url)
    # print(url)
    # print()
    # pprint.pprint(resp.status_code)
    # print()
    # pprint.pprint(resp.headers)
    # print()
    # print(resp.json())



id_systems = [
    30000001,
    30000002,
    30000003,
    30000004,
    300000040,
    300000050,
    30000006,
    30000007,
    30000008,
    30000009,
    30000010,
]
