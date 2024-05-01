"""
Отдельный парсер одного релейта и парсер всех связанных с релейтом сущностей.
"""
from asgiref.sync import sync_to_async

from dbeve_social.models import *

from .parser_main import GET_request_to_esi, create_all_entities
from .enter_entitys_to_db import enter_entitys_to_db


# async def create_linking_entities(related_id):
#     """
#     После создания киллмыл, создаем все упомянутые в релейте корпы, альянсы, чары 
#     все они создаются с флагом create_missing - чтобы не гонять лишние запросы
#
#     Также после создания этих сущностей, они подлинковываются к киллмылу. Внутренние 
#     связи сущностей (корпа к альянсу или чар к корпе - они выполняются внутри их парсеров)
#     """
#
#     @sync_to_async
#     def get_killmails(related_id):
#         """
#         Для изоляции запроса в бд внтури функции sync_to_async
#         """
#         killmails = Relates.objects.get(related_id=related_id).killmails.all()
#         # в этом месте выполняется собственно запрос в БД
#         killmails = list(killmails)
#         return killmails
#
#     alliances_ids = []
#     corporations_ids = []
#     characters_ids = []
#     
#     killmails = await get_killmails(related_id)
#
#     for killmail in killmails:
#         attackers = killmail.response_body["esi_data"]["attackers"]
#         victim = killmail.response_body["esi_data"]["victim"]
#         # не забыать, что в киллмыле могут быть неписи - похоже что исключительно на стороне атакующих
#         # не забывать что кто нибудь может не быть в альянсе
#         # не забывать, что среди жертв и атакующих могут быть структуры - тогда у них не будет чара
#
#         # альянсы атакующих и жертвы
#         attackers_alliances_ids = [attacker.get("alliance_id") for attacker in attackers]
#         alliances_ids.append(victim.get("alliance_id"))
#         alliances_ids.extend(attackers_alliances_ids)
#
#         # корпорации атакующих и жертвы
#         attackers_corporations_ids = [attacker.get("corporation_id") for attacker in attackers]
#         corporations_ids.append(victim.get("corporation_id"))
#         corporations_ids.extend(attackers_corporations_ids)
#
#         # чары атакующих и жертвы
#         attackers_characters_ids = [attacker.get("character_id") for attacker in attackers]
#         characters_ids.append(victim.get("character_id"))
#         characters_ids.extend(attackers_characters_ids)
#
#     alliances_ids = list(set(alliances_ids))
#     corporations_ids = list(set(corporations_ids))
#     characters_ids = list(set(characters_ids))
#     # избавляемся от None - они встречаются достаточно часто
#     alliances_ids = [alliance_id for alliance_id in alliances_ids if alliance_id ]
#     corporations_ids = [corporation_id for corporation_id in corporations_ids if corporation_id ]
#     characters_ids = [character_id for character_id in characters_ids if character_id ]
#
#     # создаем связанные записи
#     await create_all_entities("only_missing", "alliance", alliances_ids)
#     await create_all_entities("only_missing", "corporation", corporations_ids)
#     await create_all_entities("only_missing", "character", characters_ids)
#     
#     # линковка киллмыл с вновь созданными сопуствующими сущностями
#     print(f"Start linking killmails")
#     await linking_killmails(killmails)
#     print(f"Successful linking killmails")
#

async def create_related(related_id):
    """
    Парсит один релейт. Сначала загружает общую инфу с br.eveotools.org
    создает запись в БД с ним, потом выделяет из релейта все киллмыла 
    и запускает для них killmails_parser.

    Обернута транзакцией, т.к. внутри много запросов и линковки.
    """
    url = "https://br.evetools.org/api/v1/composition/get/" + related_id

    print(f"Start load related {related_id}")
    compose_related = GET_request_to_esi(url).json()
    print(f"Successfull load related {related_id}")

    # дополянем релейт ссылкой и формируем стандартный вид данных для сохранения - ключ_id_сущности:результат запроса
    compose_related["url"] = url
    response = {f"{related_id}": compose_related}
    await enter_entitys_to_db("related", response)

    # # ключи прочитал в на json-ответах от br.evetools.com
    # # в сборном релейте отдельные релейты по системам лежат в общем списке
    # killmails = []
    # relateds = compose_related["relateds"]
    # for related in relateds:
    #     killmails.extend(related["kms"])
    #
    # killmails_ids = []
    # for killmail in killmails:
    #     killmails_ids.append(killmail["id"])
    #
    # # загрузка с esi всех связанных с релейтом дополнитеьных данных
    # print("Start of loading alliances, corporations, and characters associated with this related.")
    # await create_linking_entities(related_id)
    # print(f"Successfull load associated data.")

