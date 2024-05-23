"""
Отдельный парсер одного релейта и парсер всех связанных с релейтом сущностей.
"""
import pprint
from asgiref.sync import sync_to_async

from dbeve_social.models import *

from .parser_main import GET_request_to_esi, create_all_entities
from .enter_entitys_to_db import enter_entitys_to_db
from .conf import action_list_type

@sync_to_async
def get_ids_associated_entities_from_battlereport(battlereport_id):
    """
    Получает id бра, выделяет списки всех альянсов, корп, чаров - и жертвы
    и атакующих, после чего возвращает эти списки вместе с ключом киллмыла - 
    для последующей удобной линковки.
    """
    battlereport = Battlereports.objects.get(battlereport_id=battlereport_id)
    relateds = [related for related in battlereport.response_body["relateds"]]
    killmails = []
    for related in relateds:
        killmails.extend(related["kms"])

    alliances_ids = []
    corporations_ids = []
    characters_ids = []
    for killmail in killmails:
        alliances_ids.append(killmail["vict"].get("ally"))
        corporations_ids.append(killmail["vict"].get("corp"))
        characters_ids.append(killmail["vict"].get("char"))
        for attacker in killmail["atts"]:
            alliances_ids.append(attacker.get("ally"))
            corporations_ids.append(attacker.get("corp"))
            characters_ids.append(attacker.get("char"))

    # удаление дублей и значений-заглушек (заглушки - вместо id у нпс-атакующих, структур и подобного)
    errors_ids = set([0, None])

    alliances_ids = set(alliances_ids)
    corporations_ids = set(corporations_ids)
    characters_ids = set(characters_ids)

    alliances_ids.difference_update(errors_ids)
    corporations_ids.difference_update(errors_ids)
    characters_ids.difference_update(errors_ids)

    alliances_ids = list(alliances_ids)
    corporations_ids = list(corporations_ids)
    characters_ids = list(characters_ids)

    return alliances_ids, corporations_ids, characters_ids

@sync_to_async
def linking_killmail_and_victim(victim:Victims):
    """
    Получает экземпляр Victims, выполняет множество линковок
    """
    alliance_id = victim.response_body["ally"]
    corporation_id = victim.response_body["corp"]
    character_id = victim.response_body["char"]
    ship_id = victim.response_body["ship"]
    killmail_id = victim.response_body["kml_id"]

    alliance = Alliances.objects.get(alliance_id=alliance_id)
    corporation = Corporations.objects.get(corporation_id=corporation_id)
    character = Characters.objects.get(character_id=character_id)
    ship = Types.objects.get(type_id=ship_id)
    killmail = Killmails.objects.get(killmail_id=killmail_id)

    victim.alliance = alliance
    victim.corporation = corporation
    victim.character = character
    victim.ship = ship
    victim.killmail = killmail

    victim.save()

@sync_to_async
def linking_battlereport_and_killmails(battlereport_id, killmails_ids):
    """
    связывает киллмыла и бр
    """
    battlereport = Battlereports.objects.get(battlereport_id=battlereport_id)
    killmails = Killmails.objects.filter(killmail_id__in=killmails_ids)
    for killmail in killmails:
        killmail.battlereports.add(battlereport)
        killmail.save()


async def create_and_linking_victims(killmails_ids):
    """
    Создаем экземпляры Victim и линковка киллмыл с ними. 
    Под атакующих не нужно отдельную модель - слишком много бесполезных
    записей в БД получается. Пусть хранятся в br_data как json.
    """
    @sync_to_async
    def get_killmails(killmails_ids):
        """
        Для изоляции запроса в бд внтури функции sync_to_async
        """
        killmails = Killmails.objects.filter(killmail_id__in=killmails_ids)
        return list(killmails)

    killmails = await get_killmails(killmails_ids)

    victim_data = {}
    for killmail in killmails:
        br_data = killmail.response_body["br_data"]
        victim = br_data["vict"]
        # вручную формируем id жертвы из id киллмыла и id чара
        victim_id = str(killmail.killmail_id) + "_" + str(victim.get("char"))
        # вручную добавляем id киллмыла в будущий response_body
        victim["kml_id"] = killmail.killmail_id
        victim["victim_id"] = victim_id
        victim_data[victim_id] = victim

    victims = await enter_entitys_to_db("victim", victim_data)

    for victim_key in victims.keys():
        victim = victims[victim_key]
        await linking_killmail_and_victim(victim)





async def create_associated_entities(battlereport_id):
    """
    Затрагивает киллмыла, алли, корпы, чары упомянутые в бр-е.

    Создаем киллмыла, слинковываем их с релейтом.

    После создания киллмыл, создаем все упомянутые в релейте корпы, альянсы, чары 
    все они создаются с флагом create_missing - чтобы не гонять лишние запросы
    """

    @sync_to_async
    def get_battlereport(battlereport_id):
        """
        Для изоляции запроса в бд внтури функции sync_to_async
        """
        battlereport = Battlereports.objects.get(battlereport_id=battlereport_id)
        return battlereport

    battlereport = await get_battlereport(battlereport_id)

    # создаем киллмыла на основе бр-а
    relateds = battlereport.response_body["relateds"]
    temp_killmails = []
    for related in relateds:
        temp_killmails.extend(related["kms"])
    killmails = {killmail["id"]:killmail for killmail in temp_killmails}
    await enter_entitys_to_db("killmail_from_br", killmails)

    # это самый простой способ получить id всех киллмыл релейта, в данном случае конечно
    killmails_ids = killmails.keys()

    # запускаем линковку киллмыл с бр-ом
    print("Start linking killmail and battlereport.")
    await linking_battlereport_and_killmails(battlereport_id, killmails_ids)
    print("Successful linking killmail and battlereport.")


    # получаем id алли, корп, чаров на основе уже записанного в БД бр-а. 
    alliances_ids, corporations_ids, characters_ids = await get_ids_associated_entities_from_battlereport(battlereport_id)

    # создаем связанные записи
    await create_all_entities("only_missing", "alliance", alliances_ids)
    await create_all_entities("only_missing", "corporation", corporations_ids)
    await create_all_entities("only_missing", "character", characters_ids)

    # линковка киллмыл с вновь созданными сопуствующими сущностями
    print(f"Start linking killmails")
    await create_and_linking_victims(killmails_ids)
    print(f"Successful linking killmails")


async def create_battlereport(battlereport_id):
    """
    Парсит один бр. После сохранения бр-а создает 
    ограниченную запись киллмыла (без хэша) и начинет 
    парсить все связанные с ним сущности (алли, корпы, чары).

    """
    @sync_to_async
    def check_exists_br(battlereport_id):
        try:
            Battlereports.objects.get(battlereport_id=battlereport_id)
            return True
        except Battlereports.DoesNotExist:
            return False

    # if await check_exists_br(battlereport_id):
    #     print(f"Battlereport {battlereport_id} is exist.")
    #     # загрузка с esi всех связанных с релейтом дополнитеьных данных
    #     print("Start of loading alliances, corporations, and characters associated with this battlereport.")
    #     await create_associated_entities(battlereport_id)
    #     print(f"Successfull load associated data.")
    #     return

    # всегда использовать шорт-вариант - не-шорт вариант иногда отдает тот же шорт.
    url = f"https://br.evetools.org/api/v1/composition/get/{battlereport_id}/?short=true"

    print(f"Start load battlereport {battlereport_id}")
    battlereport = GET_request_to_esi(url).json()
    print(f"Successfull load battlereport {battlereport_id}")


    # дополянем релейт ссылкой и формируем стандартный вид данных для сохранения - ключ_id_сущности:результат запроса
    battlereport["url"] = url
    response = {f"{battlereport_id}": battlereport}
    await enter_entitys_to_db("battlereport", response)

    # загрузка с esi всех связанных с релейтом дополнитеьных данных
    print("Start of loading alliances, corporations, and characters associated with this battlereport.")
    await create_associated_entities(battlereport_id)
    print(f"Successfull load associated data.")

