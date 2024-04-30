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
def linking_constellations(list_of_entities=None):
    """
    Из внешних ключей только ссылка на регион.
    """
    if not list_of_entities:
        constellations = Constellations.objects.all()
    else:
        constellations = Constellations.objects.filter(constellation_id__in=list_of_entities)
    count = 1
    l = len(constellations)
    for constellation in constellations:
        region = Regions.objects.get(region_id=constellation.response_body["region_id"])
        constellation.region = region
        constellation.save(update_fields=["region",])
        print(f"Link {constellation.constellation_id} constellations. {count}/{l}")
        count += 1


@sync_to_async
def linking_systems(list_of_entities=None):
    """
    Формирование внешиних связей у систем.
    Только ссылка на констелляцию.
    """
    if not list_of_entities:
        systems = Systems.objects.all()
    else:
        systems = Systems.objects.filter(system_id__in=list_of_entities)
    count = 1
    l = len(systems)
    for system in systems:
        constellation = Constellations.objects.get(constellation_id=system.response_body["constellation_id"])
        system.constellation = constellation
        system.save(update_fields=["constellation",])
        print(f"Link {system.system_id} system. {count}/{l}")
        count += 1


@sync_to_async
def linking_stars(list_of_entities=None):
    """
    Связи у звезд.
    """
    if not list_of_entities:
        stars = Stars.objects.all()
    else:
        stars = Stars.objects.filter(star_id__in=list_of_entities)
    count = 1
    l = len(stars)
    for star in stars:
        system = Systems.objects.get(system_id=star.response_body["solar_system_id"])
        star.solar_system = system
        star.save(update_fields=["solar_system",])
        print(f"Link {star.star_id} star. {count}/{l}")
        count += 1


@sync_to_async
def linking_corporations(list_of_entities=None):
    """
    Связи у корпораций. Возможно сначала не все.
    """
    if not list_of_entities:
        corporations = Corporations.objects.all()
    else:
        corporations = Corporations.objects.filter(corporation_id__in=list_of_entities)
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
def linking_groups(list_of_entities=None):
    """
    Связи у групп итемов.
    """
    if not list_of_entities:
        groups = Groups.objects.all()
    else:
        groups = Groups.objects.filter(group_id__in=list_of_entities)
    count = 1
    l = len(groups)
    for group in groups:
        category = Categories.objects.get(category_id=group.response_body["category_id"])
        group.category = category
        group.save(update_fields=["category",])
        print(f"Link {group.group_id} group. {count}/{l}")
        count += 1


@sync_to_async
def linking_types(list_of_entities=None):
    """
    Связи у типов итемов.
    """
    if not list_of_entities:
        types = Types.objects.all()
    else:
        types = Types.objects.filter(type_id__in=list_of_entities)
    count = 1
    l = len(types)
    for type_item in types:
        group = Groups.objects.get(group_id=type_item.response_body["group_id"])
        type_item.group = group
        type_item.save(update_fields=["group",])
        print(f"Link {type_item.type_id} type. {count}/{l}")
        count += 1


@sync_to_async
def linking_relates(killmails_ids, related_id):
    """
    Линковка киллмыл к релейту
    """
    related = Relates.objects.get(related_id=related_id)
    for killmail_id in killmails_ids:
        killmail = Killmails.objects.get(killmail_id=killmail_id)
        related.killmails.add(killmail)


@sync_to_async
def linking_killmails(killmails):
    """
    Получает не просто список id, а список уже выбранных из БД киллмыл.
    Подлинковка к всем киллмылам связанных данных.
    В первую очередь - алли, корпа, чар жертвы.
    """
    for killmail in killmails:
        esi_data = killmail.response_body["esi_data"]

        alliance_id = esi_data["victim"].get("alliance_id")
        corporation_id = esi_data["victim"].get("corporation_id")
        character_id = esi_data["victim"].get("character_id")
        type_id = esi_data["victim"].get("ship_type_id")

        try:
            victim_alliance = Alliances.objects.get(alliance_id=alliance_id)
        except Alliances.DoesNotExist:
            victim_alliance = None

        try:
            victim_corporation = Corporations.objects.get(corporation_id=corporation_id)
        except Corporations.DoesNotExist:
            victim_corporation = None

        try:
            victim_character = Characters.objects.get(character_id=character_id)
        except Characters.DoesNotExist:
            victim_character = None

        try:
            victim_ship_type = Types.objects.get(type_id=type_id)
        except Types.DoesNotExist:
            victim_ship_type = None


        killmail.victim_alliance = victim_alliance
        killmail.victim_corporation = victim_corporation
        killmail.victim_character = victim_character
        killmail.victim_ship_type = victim_ship_type

        killmail.save()

