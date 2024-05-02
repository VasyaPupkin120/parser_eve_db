"""
Отдельный парсер одного релейта и парсер всех связанных с релейтом сущностей.
"""
from asgiref.sync import sync_to_async

from dbeve_social.models import *

from .parser_main import GET_request_to_esi, create_all_entities
from .enter_entitys_to_db import enter_entitys_to_db

def get_allinaces_from_battlereport(battlereport):
    """
    Получает список словарей-киллмыл, выделяет список всех альянсов, 
    возвращает его.
    """


async def create_linking_entities(battlereport_id):
    """
    После создания киллмыл, создаем все упомянутые в релейте корпы, альянсы, чары 
    все они создаются с флагом create_missing - чтобы не гонять лишние запросы

    Также после создания этих сущностей, они подлинковываются к киллмылу. Внутренние 
    связи сущностей (корпа к альянсу или чар к корпе - они выполняются внутри их парсеров)
    """

    @sync_to_async
    def get_battlereport(battlereport_id):
        """
        Для изоляции запроса в бд внтури функции sync_to_async
        """
        battlereport = Battlereports.objects.get(battlereport_id=battlereport_id)
        return battlereport

    battlereport = await get_battlereport(battlereport_id)

    relateds = []
    [relateds.extend(related) for related in battlereport.response_body["relateds"]]
    killmails = []
    print(relateds)

    # [killmails.extend(related["kms"]) for related in relateds ]
    # print("linking entities: ", len(killmails), "br_kmsCount: ", battlereport.kmsCount)


    # alliances_ids = get_allinaces_from_battlereport(battlereport)
    # corporations_ids = get_corporations_from_battlereport(battlereport)
    # characters_ids = get_characters_from_battlereport(battlereport)
    # 
    #
    # for killmail in killmails:
    #     attackers = killmail.response_body["esi_data"]["attackers"]
    #     victim = killmail.response_body["esi_data"]["victim"]
    #     # не забыать, что в киллмыле могут быть неписи - похоже что исключительно на стороне атакующих
    #     # не забывать что кто нибудь может не быть в альянсе
    #     # не забывать, что среди жертв и атакующих могут быть структуры - тогда у них не будет чара
    #
    #     # альянсы атакующих и жертвы
    #     attackers_alliances_ids = [attacker.get("alliance_id") for attacker in attackers]
    #     alliances_ids.append(victim.get("alliance_id"))
    #     alliances_ids.extend(attackers_alliances_ids)
    #
    #     # корпорации атакующих и жертвы
    #     attackers_corporations_ids = [attacker.get("corporation_id") for attacker in attackers]
    #     corporations_ids.append(victim.get("corporation_id"))
    #     corporations_ids.extend(attackers_corporations_ids)
    #
    #     # чары атакующих и жертвы
    #     attackers_characters_ids = [attacker.get("character_id") for attacker in attackers]
    #     characters_ids.append(victim.get("character_id"))
    #     characters_ids.extend(attackers_characters_ids)
    #
    # alliances_ids = list(set(alliances_ids))
    # corporations_ids = list(set(corporations_ids))
    # characters_ids = list(set(characters_ids))
    # # избавляемся от None - они встречаются достаточно часто
    # alliances_ids = [alliance_id for alliance_id in alliances_ids if alliance_id ]
    # corporations_ids = [corporation_id for corporation_id in corporations_ids if corporation_id ]
    # characters_ids = [character_id for character_id in characters_ids if character_id ]
    #
    # # создаем связанные записи
    # await create_all_entities("only_missing", "alliance", alliances_ids)
    # await create_all_entities("only_missing", "corporation", corporations_ids)
    # await create_all_entities("only_missing", "character", characters_ids)
    # 
    # # линковка киллмыл с вновь созданными сопуствующими сущностями
    # print(f"Start linking killmails")
    # await linking_killmails(killmails)
    # print(f"Successful linking killmails")


async def create_battlereport(battlereport_id):
    """
    Парсит один релейт. После сохранения релейта начинает
    парсить все связанные с ним сущности (алли, корпы, чары).
    """
    url = "https://br.evetools.org/api/v1/composition/get/" + battlereport_id

    print(f"Start load battlereport {battlereport_id}")
    compose_battlereport = GET_request_to_esi(url).json()
    print(f"Successfull load battlereport {battlereport_id}")

    # дополянем релейт ссылкой и формируем стандартный вид данных для сохранения - ключ_id_сущности:результат запроса
    compose_battlereport["url"] = url
    response = {f"{battlereport_id}": compose_battlereport}
    await enter_entitys_to_db("battlereport", response)

    # загрузка с esi всех связанных с релейтом дополнитеьных данных
    print("Start of loading alliances, corporations, and characters associated with this battlereport.")
    await create_linking_entities(battlereport_id)
    print(f"Successfull load associated data.")

