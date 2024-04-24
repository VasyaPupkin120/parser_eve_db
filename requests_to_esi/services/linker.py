"""
Создание связей между моделями.
Т.к. будут выполняться внутри асинхронных функций и есть записи в БД,
то все линкеры также должны быть асинхронными.
"""
from asgiref.sync import sync_to_async
from dbeve_universe.models import *
from dbeve_social.models import *
from dbeve_items.models import *

# у регионов, у категорий итемов нет внешних ключей, это что то вроде корневой модели.

@sync_to_async
def linking_constellations():
    """
    Из внешних ключей только ссылка на регион.
    """
    constellations = Constellations.objects.all()
    count = 1
    l = len(constellations)
    for constellation in constellations:
        region = Regions.objects.get(region_id=constellation.response_body["region_id"])
        constellation.region = region
        constellation.save(update_fields=["region",])
        print(f"Link {constellation.constellation_id} constellations. {count}/{l}")
        count += 1


@sync_to_async
def linking_systems():
    """
    Формирование внешиних связей у систем.
    Только ссылка на констелляцию.
    """
    systems = Systems.objects.all()
    count = 1
    l = len(systems)
    for system in systems:
        constellation = Constellations.objects.get(constellation_id=system.response_body["constellation_id"])
        system.constellation = constellation
        system.save(update_fields=["constellation",])
        print(f"Link {system.system_id} system. {count}/{l}")
        count += 1


@sync_to_async
def linking_stars():
    """
    Связи у звезд.
    """
    stars = Stars.objects.all()
    count = 1
    l = len(stars)
    for star in stars:
        system = Systems.objects.get(system_id=star.response_body["solar_system_id"])
        star.solar_system = system
        star.save(update_fields=["solar_system",])
        print(f"Link {star.star_id} star. {count}/{l}")
        count += 1


@sync_to_async
def linking_corporations():
    """
    Связи у корпораций. Возможно сначала не все.
    """
    corporations = Corporations.objects.all()
    count = 1
    l = len(corporations)
    for corporation in corporations:
        alliance_id=corporation.response_body.get("alliance_id")
        if not alliance_id:
            print(f"Corporation {corporation.corporation_id} not in alliance.")
            continue
        alliance = Alliances.objects.get(alliance_id=alliance_id)
        corporation.alliance = alliance
        corporation.save(update_fields=["alliance",])
        print(f"Link {corporation.corporation_id} corporation. {count}/{l}")
        count += 1


@sync_to_async
def linking_groups():
    """
    Связи у групп итемов.
    """
    groups = Groups.objects.all()
    count = 1
    l = len(groups)
    for group in groups:
        category = Categories.objects.get(category_id=group.response_body["category_id"])
        group.category = category
        group.save(update_fields=["category",])
        print(f"Link {group.group_id} group. {count}/{l}")
        count += 1


@sync_to_async
def linking_types():
    """
    Связи у типов итемов.
    """
    types = Types.objects.all()
    count = 1
    l = len(types)
    for type_item in types:
        group = Groups.objects.get(group_id=type_item.response_body["group_id"])
        type_item.group = group
        type_item.save(update_fields=["group",])
        print(f"Link {type_item.type_id} type. {count}/{l}")
        count += 1
