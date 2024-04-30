import time
import aiohttp
from asgiref.sync import sync_to_async

from django.db import transaction, IntegrityError

from . import errors
from .base_requests import several_async_requests, GET_request_to_esi, get_urls
from .enter_entitys_to_db import enter_entitys_to_db
from .asynctimer import async_timed
from .conf import NUMBER_OF_REQUEST, action_list_type, entity_list_type
from .linker import *
from .formed_list_ids import formed_list_ids_to_enter_in_DB

from dbeve_universe.models import *
from dbeve_social.models import *


def create_chunks(ids:list, entity:entity_list_type):
    """
    принимает большой список ids, возвращает список разбитый на чанки - тоже списки.
    Размер чанка определяется NUMBER_OF_REQUEST.
    В последнем чанке остатки.
    """
    if entity == "killmail_evetools":
        value_chunk = 10
    else:
        value_chunk = NUMBER_OF_REQUEST
        

    ids_chunks = []
    temp = []
    for count, id_key in enumerate(ids):
        if count % value_chunk == 0 and count != 0:
            ids_chunks.append(temp) 
            temp = []
        temp.append(id_key) 
    ids_chunks.append(temp) 
    return ids_chunks



async def linking(entity:entity_list_type, list_of_entities):
    """
    Линковка для тех сущностей, которым она нужна.
    """
    if entity == "constellation":
        await linking_constellations(list_of_entities)
    elif entity == "system":
        await linking_systems(list_of_entities)
    elif entity == "star":
        await linking_stars()
    elif entity == "corporation":
        await linking_corporations(list_of_entities)
    elif entity == "group":
        await linking_groups(list_of_entities)
    elif entity == "type":
        await linking_types(list_of_entities)
    else:
        print(f"Linking for the {entity}s is not needed or the method is not defined.")



@async_timed()
async def create_all_entities(
        action:action_list_type,
        entity:entity_list_type,
        list_of_entities:list|None=None,
        **kwargs,
        ):
    """
    Главная функция-парсер, все остальные - вспомогательные или независмые.

    Определяет список id по которым нужно запросить инфу в esi,
    запрашивает инфу по этим id из esi, вносит эту инфу в БД.

    Если нужно внести данные не по целой модели а дополнить поле модели, эта функция
    тоже пригодна, просто нужно задать сущность для этого действия и для этой сущности
    определить нужные действия в функции enter_entitys_to_db() - т.е. не сохранять 
    все поля, а обновить только одно. Внутренние id для этой цели можно 
    выставлять пустыми - [] в функции управляющей выделением внутренних id.

    если нужно выполнить парсинг не всех сущностей, а только ограниченного набора,
    то набор их id можно передать в list_of_entites - он будет считаться внешними
    id.

    **kwargs может быть нужно для передачи каких то данных в каких то случаях 
    например, когда нужно передать related_id в функцию enter_entitys_to_db
    """
    # проверка сущностей и действий
    errors.check_action(action)
    errors.check_entity(entity)

    # формирование списка id, по которым нужно обращаться в esi и запрашивать инфу
    id_for_enter_to_db = await formed_list_ids_to_enter_in_DB(action, entity, list_of_entities)
    if not id_for_enter_to_db:
        print("\nThere are no IDs that need to be entered into the database\n")
        return

    # разбиение списка id на чанки
    chunks = create_chunks(id_for_enter_to_db, entity)

    # старт загрузки данных с esi и сохранение в БД
    print(f"\nStart loading information about the {entity} from the ESI and saving it into the database")
    count = 0
    async with aiohttp.ClientSession() as session:
        for chunk in chunks:
            print(f"\nLoad {count * NUMBER_OF_REQUEST}/{len(id_for_enter_to_db)} {entity}s")
            data = await several_async_requests(session, chunk, entity)
            await enter_entitys_to_db(entity, data, **kwargs)
            # задержка не особо чет помогает от множества ошибок сервера esi при загрузке истории нахождения чара в корпорациях.
            # await asyncio.sleep(0.5)
            count += 1
    print("Successful downloading and saving information by {entity}.")

    # запуск линковки
    await linking(entity, list_of_entities)


async def create_killmails(killmails_ids, related_id):
    """
    Киллмыло зависит от множества подзапросов - в частности запросы по 
    персонажам, по их корпам и алли.

    Эта функция работает в несколько заходов 
    сначала создание собственно киллмыл на основе api evetools, 
    потом на основе этих записей выполянется запрос в esi по этому же киллмылу,
    потом на основе ответа из esi - множество запросов по чарам и корпам,
    потом линковка этого всего.

    Идшник релейта related_id ВНОСИТСЯ в поле response_body в функции enter_entitys_to_db
    при самом первом запросе данных с evetools - вместе с телом первого запроса.  
    В во втором запросе инфы по киллмылу (с esi) поле response_body именно что ДОПОЛНЯЕТСЯ. 
    Это важно - всегда сначала должен идти зпрос evetools, и только потом esi. 
    (первопричина в том, что хэш киллмыла можно получить тоько при запросе отдельного киллмыла в evetools).
    Значение передается через ключевые параметры **kwargs.
    """
    # zkb не хочет отдавать запросы параллельно
    # вместо zkb буду использовать api от evetools
    # запрашиваем хэш киллмыла и что нибудь дополнительное 
    print(f"Start load base information killmails from br.evetools.com.")
    await create_all_entities("only_missing", "killmail_evetools", killmails_ids, related_id=related_id)
    print(f"Successful load base information killmails from br.evetools.com.")

    # связываем килмыла с релейтом
    print(f"Start linking related and killmails.")
    await linking_relates(killmails_ids, related_id)
    print(f"Successful linking related and killmails.")

    # запрашиваем полную инфу от esi. Внутренними будут считаться те записи,
    # в которых заполнено поле killmail_time - оно заполняется именно при запросе к esi
    print(f"Start load full information killmails from ESI.")
    await create_all_entities("only_missing", "killmail_esi", killmails_ids)
    print(f"Successful load full information killmails from ESI.")


async def create_linking_entities(related_id):
    """
    После создания киллмыл, создаем все упомянутые в релейте корпы, альянсы, чары 
    все они создаются с флагом create_missing - чтобы не гонять лишние запросы

    Также после создания этих сущностей, они подлинковываются к киллмылу. Внутренние 
    связи сущностей (корпа к альянсу или чар к корпе - они выполняются внутри их парсеров)
    """

    @sync_to_async
    def get_killmails(related_id):
        """
        Для изоляции запроса в бд внтури функции sync_to_async
        """
        killmails = Relates.objects.get(related_id=related_id).killmails.all()
        # в этом месте выполняется собственно запрос в БД
        killmails = list(killmails)
        return killmails

    alliances_ids = []
    corporations_ids = []
    characters_ids = []
    
    killmails = await get_killmails(related_id)

    for killmail in killmails:
        attackers = killmail.response_body["esi_data"]["attackers"]
        victim = killmail.response_body["esi_data"]["victim"]
        # не забыать, что в киллмыле могут быть неписи - похоже что исключительно на стороне атакующих
        # не забывать что кто нибудь может не быть в альянсе
        # не забывать, что среди жертв и атакующих могут быть структуры - тогда у них не будет чара

        # альянсы атакующих и жертвы
        attackers_alliances_ids = [attacker.get("alliance_id") for attacker in attackers]
        alliances_ids.append(victim.get("alliance_id"))
        alliances_ids.extend(attackers_alliances_ids)

        # корпорации атакующих и жертвы
        attackers_corporations_ids = [attacker.get("corporation_id") for attacker in attackers]
        corporations_ids.append(victim.get("corporation_id"))
        corporations_ids.extend(attackers_corporations_ids)

        # чары атакующих и жертвы
        attackers_characters_ids = [attacker.get("character_id") for attacker in attackers]
        characters_ids.append(victim.get("character_id"))
        characters_ids.extend(attackers_characters_ids)

    alliances_ids = list(set(alliances_ids))
    corporations_ids = list(set(corporations_ids))
    characters_ids = list(set(characters_ids))
    # избавляемся от None - они встречаются достаточно часто
    alliances_ids = [alliance_id for alliance_id in alliances_ids if alliance_id ]
    corporations_ids = [corporation_id for corporation_id in corporations_ids if corporation_id ]
    characters_ids = [character_id for character_id in characters_ids if character_id ]

    # создаем связанные записи
    await create_all_entities("only_missing", "alliance", alliances_ids)
    await create_all_entities("only_missing", "corporation", corporations_ids)
    await create_all_entities("only_missing", "character", characters_ids)
    
    # линковка киллмыл с вновь созданными сопуствующими сущностями
    print(f"Start linking killmails")
    await linking_killmails(killmails)
    print(f"Successful linking killmails")



@transaction.atomic
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

    # ключи прочитал в на json-ответах от br.evetools.com
    # в сборном релейте отдельные релейты по системам лежат в общем списке
    killmails = []
    relateds = compose_related["relateds"]
    for related in relateds:
        killmails.extend(related["kms"])

    killmails_ids = []
    for killmail in killmails:
        killmails_ids.append(killmail["id"])

    # создание всех киллмыл, связанных с релейтом
    print(f"Start load killmails in related.")
    await create_killmails(killmails_ids, related_id)
    print(f"Successfull load killmails in related.")

    # загрузка с esi всех связанных с релейтом дополнитеьных данных
    print("Start of loading alliances, corporations, and characters associated with this related.")
    await create_linking_entities(related_id)
    print(f"Successfull load associated data.")

