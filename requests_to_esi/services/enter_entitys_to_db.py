from asgiref.sync import sync_to_async
import datetime


from .errors import raise_entity_not_processed, raise_action_not_allowed
from .base_requests import GET_request_to_esi
from .conf import entity_list_type

from dbeve_social.models import Alliances, Characters, Corporations, Killmails, Battlereports, Victims, Attackers
from dbeve_universe.models import Constellations, Regions, Stars, Systems
from dbeve_items.models import Categories, Groups, Types



################################################################################
#              очень большая функция-креатор, но альтернатива -                #
#               очень много маленьких однообразных функций                     #
#     сложно придумать обобщенный вариант из-за разных имен полей в моделях    #
################################################################################


# пришлось преобразовать enter_entitys_to_db в асинхронную, т.к. иначе запись в БД
# вызывала ошибку django.core.exceptions.SynchronousOnlyOperation
# соответсвенно, ее нужно вызывать через await
@sync_to_async
def enter_entitys_to_db(
        entity: entity_list_type,
        data:dict,
        **kwargs
        ):
    """
    Исключительно для сохранения данных в БД. Получает словарь и сохраняет данные из него в БД.

    Функция получает тип сущности и словарь с данными и вносит данные по 
    значению в БД. Количество записей в словаре зависит от размера чанка.
    data - словарь, полученный из функции several_async_requests

    словарь вида:
    {
        entity_id1: {name_field1: data, name_field2: data, ...},
        entity_id2: {name_field1: data, name_field2: data, ...}
    }

    Не выполняет связывание записей - линковка выполняется отдельной функцией.
    В том числе для альянсов не выполняется подгрузка ассоциированных корпораций - 
    это делать отдельно, в функции внешних id для корпораций.

    Функция не занимается загрузкой и сохранением изображений. Это нужно как-то
    отдельно делать.

    Возвращает словарь, в котором ключи совпадают с входными ключами, а значения - объекты 
    записей БД. Для случаев, когда записи не создаются а только дополняются - то ничего не 
    возвращается.

    **kwargs используется для каких то частных случаев, например передает id релейта
    для каждого киллмыла - исключительно для дополнения поля response_body.
    """

    # LSP ругается, но все работает. Эта проверка нужна, 
    # чтобы не выполнять впустую запросы для ошибочных параметров
    if entity not in entity_list_type.__args__:
        raise_entity_not_processed(entity)

    # словарь для возврата только что созданных записей, может быть нужно или не нужно
    return_data = {}

    # запись данных по региону
    if entity == "region":
        for key in data:
            new_entity = Regions.objects.update_or_create(
                    region_id=key,
                    defaults={
                        "region_id": key,
                        "name": data[key].get("name"),
                        "description": data[key].get("description"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись данных по констелляции
    elif entity == "constellation":
        for key in data:
            new_entity = Constellations.objects.update_or_create(
                    constellation_id=key,
                    defaults={
                        "constellation_id": key,
                        "name": data[key].get("name"),
                        "position_x": data[key].get("position")["x"],
                        "position_y": data[key].get("position")["y"],
                        "position_z": data[key].get("position")["z"],
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись данных по системе
    elif entity == "system":
        for key in data:
            new_entity = Systems.objects.update_or_create(
                    system_id=key,
                    defaults={
                        "name": data[key].get("name"),
                        "position_x": data[key].get("position")["x"],
                        "position_y": data[key].get("position")["y"],
                        "position_z": data[key].get("position")["z"],
                        "security_class": data[key].get("security_class"),
                        "security_status": data[key].get("security_status"),
                        "system_id": key,
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись данных по звезде
    elif entity == "star":
        for key in data:
            new_entity = Stars.objects.update_or_create(
                    star_id=key,
                    defaults={
                        "age": data[key].get("age"),
                        "luminosity": data[key].get("luminosity"),
                        "name": data[key].get("name"),
                        "radius": data[key].get("radius"),
                        "spectral_class": data[key].get("spectral_class"),
                        "star_id": key,
                        "temperature": data[key].get("temperature"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись данных по альянсу
    elif entity == "alliance":
        for key in data:
            new_entity = Alliances.objects.update_or_create(
                    alliance_id=key,
                    defaults={
                        "alliance_id": key,
                        "date_founded": data[key].get("date_founded"),
                        "name": data[key].get("name"),
                        "ticker": data[key].get("ticker"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись списка id корпораций в поле response_body для альянса.
    elif entity == "load_id_associated_corporations":
        for key in data:
            alliance = Alliances.objects.get(alliance_id = key)
            alliance.response_body["associated_corp"] = data[key]
            alliance.save()
            print(f"Successful save list associated corp in alliance: {key}\n")

    # запись данных по корпорации
    elif entity == "corporation":
        for key in data:
            new_entity = Corporations.objects.update_or_create(
                    corporation_id=key,
                    defaults={
                        "corporation_id": key,
                        "date_founded": data[key].get("date_founded"),
                        "description": data[key].get("description"),
                        "member_count": data[key].get("member_count"),
                        "name": data[key].get("name"),
                        "shares": data[key].get("shares"),
                        "ticker": data[key].get("ticker"),
                        "tax_rate": data[key].get("tax_rate"),
                        "url": data[key].get("url"),
                        "war_eligible": data[key].get("war_eligible"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись отдельного персонажа, без истории корпораций пока
    elif entity == "character":
        for key in data:
            new_entity = Characters.objects.update_or_create(
                    character_id=key,
                    defaults={
                        "character_id": key,
                        "birthday": data[key].get("birthday"),
                        "description": data[key].get("description"),
                        "is_deleted": data[key].get("is_deleted"),
                        "gender": data[key].get("gender"),
                        "name": data[key].get("name"),
                        "security_status": data[key].get("security_status"),
                        "title": data[key].get("title"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись истории корпораций для персонажа. Только дополнение поля response_body
    elif entity == "load_corporation_history":
        for key in data:
            character = Characters.objects.get(character_id = key)
            character.response_body["corporation_history"] = data[key]
            character.save()
            print(f"Successful save corporation history for character: {key}\n")

    # запись категории итемов
    elif entity == "category":
        for key in data:
            new_entity = Categories.objects.update_or_create(
                    category_id=key,
                    defaults={
                        "category_id": key,
                        "name": data[key].get("name"),
                        "published": data[key].get("published"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись группы итемов
    elif entity == "group":
        for key in data:
            new_entity = Groups.objects.update_or_create(
                    group_id=key,
                    defaults={
                        "group_id": key,
                        "name": data[key].get("name"),
                        "published": data[key].get("published"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись типа итемов
    elif entity == "type":
        for key in data:
            new_entity = Types.objects.update_or_create(
                    type_id=key,
                    defaults={
                        "capacity": data[key].get("capacity"),
                        "description": data[key].get("description"),
                        "mass": data[key].get("mass"),
                        "name": data[key].get("name"),
                        "packaged_volume": data[key].get("packaged_volume"),
                        "portion_size": data[key].get("portion_size"),
                        "published": data[key].get("published"),
                        "radius": data[key].get("radius"),
                        "response_body": data[key], 
                        "type_id": key,
                        "volume": data[key].get("volume"),
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись релейта
    elif entity == "battlereport":
        for key in data:
            new_entity = Battlereports.objects.update_or_create(
                    battlereport_id=key,
                    defaults={
                        "battlereport_id": key,
                        "kmsCount": data[key].get("kmsCount"),
                        "totalShips": data[key].get("totalShips"),
                        "totalPilots": data[key].get("totalPilots"),
                        "time_end": datetime.datetime.fromtimestamp(data[key]["ended"]), 
                        "url": data[key].get("url"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись некоторых данных по киллмылу, полученных с баттлрепорта
    # это первичное создание киллмыла
    elif entity == "killmail_from_br":
        for key in data:
            response_body = {}
            response_body["br_data"] = data[key]
            print(data[key])
            new_entity = Killmails.objects.update_or_create(
                    killmail_id=key,
                    defaults={
                        "killmail_id": key,
                        # c помощью целочисленного деления избавляемся от лишних нулей в коце, хз зачем они там
                        "killmail_time": datetime.datetime.fromtimestamp(data[key]["time"] // 1000), 
                        "sumv": data[key]["totalValue"],
                        "response_body": response_body, 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # запись данных по киллмылу, полученных с esi
    #FIXME в поле response_body слишком много дублирующейся информации. Если честно, то выглядит что нет вообще нужды в инфе от esi
    # - достаточно инфы откуда нибудь из релейта.
    elif entity == "killmail_from_esi":
        for key in data:
            # запрашиваем старое значение поля reponse_body из БД и 
            # дополняем response_body данными этого запроса - дополняем по новому ключу esi_data
            response_body = Killmails.objects.get(killmail_id=key).response_body
            response_body["esi_data"] = data[key]

            new_entity = Killmails.objects.update_or_create(
                    killmail_id=key,
                    defaults={
                        "killmail_id": key,
                        "killmail_time": datetime.datetime.strptime(data[key]["killmail_time"], "%Y-%m-%dT%H:%M:%SZ"),
                        "position_x": data[key].get("victim").get("position")["x"],
                        "position_y": data[key].get("victim").get("position")["y"],
                        "position_z": data[key].get("victim").get("position")["z"],
                        "response_body": response_body, 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}\n")
            return_data[key] = new_entity[0]
        return return_data

    # пострадавший в киллмыле. id формируется по правилу, указанному рядом с моделью  - из нескольких частей
    elif entity == "victim":
        for key in data:
            new_entity = Victims.objects.update_or_create(
                    victim_id=key,
                    defaults={
                        "dmg": data[key].get("dmg"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}")
            return_data[key] = new_entity[0]
        return return_data

    # атакущий в киллмыле
    elif entity == "attacker":
        for key in data:
            new_entity = Attackers.objects.update_or_create(
                    attacker_id=key,
                    defaults={
                        "damage_done": data[key].get("dmg"),
                        "response_body": data[key], 
                        }
                    )
            print(f"Successful save to DB {entity}: {key}")
            return_data[key] = new_entity[0]
        return return_data

    else:
        raise_entity_not_processed(entity)
