from django.core.exceptions import ObjectDoesNotExist
from .base_requests import GET_request_to_esi
from dbeve_universe.models import Regions, Constellations
from dbeve_universe.models import *
import json


# создать универсальную функцию загрузки объекта сложно - нужно как то выделить список полей которые вносить в модеь
# все подряд поля ответа вносить не получится - часть этих полей это ссылки на другие модели, которых еще нет

# выглядит как чрезмерное дублирование кода, но хз как это обойти - слишком много возни с разными полями.


def update_or_create_all_regions():
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
        update_or_create_one_region(region_id)
        count += 1

def update_or_create_one_region(region_id):
    """
    Запрашивает и обновляет (или создает) данные конкретного региона.
    """
    url = f"https://esi.evetech.net/latest/universe/regions/{region_id}/?datasource=tranquility&language=en"
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


def update_or_create_all_constellations():
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
        update_or_create_one_constellation(constellation_id)
        count += 1

def update_or_create_one_constellation(constellation_id):
    """
    выполняем запрос инфы по конкретной констелляции, сохраняем информацию в БД
    """
    url = f"https://esi.evetech.net/latest/universe/constellations/{constellation_id}/?datasource=tranquility&language=en"
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


def update_or_create_all_systems():
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
        update_or_create_one_system(system_id)
        count += 1


def update_or_create_one_system(system_id):
    """
    запрашиваем и сохраняем данные по одной системе
    """
    try:
        Systems.objects.get(system_id=system_id)
        print(f"System {system_id} already exists in DB")
        return
    except ObjectDoesNotExist:
        ...
    url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/?datasource=tranquility&language=en"
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
                "position_z": resp.get("position")["z"], "security_class": resp.get("security_class"),
                "security_status": resp.get("security_status"),
                "system_id": resp["system_id"],
                "response_body": resp,
                }
            )
    print(f"Successful save to DB system: {resp['system_id']}")


def update_or_create_all_stars():
    """
    Загружает из БД список систем, находит в response_body системы id звезды,
    выполняет запрос, создает запись звезды.

    причем что интересно, в теле ответа звезды нет информации об самой себе - об star_id
    Приходится брать star_id из информации об системе
    """
    count = 1
    star_id = None
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

        try:
            Stars.objects.get(star_id=star_id)
            print(f"Star {star_id} already exists in DB")
            count += 1
            continue
        except ObjectDoesNotExist:
            ...

        url = f"https://esi.evetech.net/latest/universe/stars/{star_id}/?datasource=tranquility"
        resp = GET_request_to_esi(url).json()
        print(f"Successful load star: {star_id}")
        Stars.objects.update_or_create(star_id=star_id,
                                       defaults={
                                           "age": resp.get("age"),
                                           "luminosity": resp.get("luminosity"),
                                           "name": resp.get("name"),
                                           "radius": resp.get("radius"),
                                           "solar_system": system,
                                           "spectral_class": resp.get("spectral_class"),
                                           "star_id": star_id,
                                           "temperature": resp.get("temperature"),
                                           "response_body": resp,
                                           }
                                       )
        print(f"Successful save to DB star: {star_id}")
        count += 1 
