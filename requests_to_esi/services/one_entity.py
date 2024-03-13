from typing import Literal

from django.core.exceptions import ObjectDoesNotExist

from .base_requests import GET_request_to_esi, load_and_save_icon, entity_not_processed, action_not_allowed
from dbeve_social.models import Alliances


###############################################################################
#                          Парсинг одной сущности.                            #
###############################################################################

entity_list_type = Literal["region", "constellation", "system", "star", "alliance", "corporation", "character"] 
action_list_type = Literal["create", "update"]

def create_or_update_one_entity(
        entity: entity_list_type,
        entity_id, 
        action: action_list_type,
        ):
    """
    Функция для первоначальной загрузки или для обновления информации
    об одной сущности.

    Режим update - это однозначно загрузить данные с esi и обновить запись. Нужно
    когда БД уже сформирована и требуется собственно обновить одну запись.

    Режим create - это проверить, есть ли такая запись в БД и если есть, 
    то не запрашивать данные с esi. Нужно для первоначального заполнения БД - 
    когда парсинг приходится запускать по несколько раз.

    соответственно, более нет необходимости в множестве функций-парсеров отдельных алли, систем и т.д.
    все это можно делать через текущую функцию.
    """

    # LSP ругается, но все работает. Эта проверка нужна, 
    # чтобы не выполнять впустую запросы для ошибочных параметров
    if entity not in entity_list_type.__args__:
        entity_not_processed(entity)
    if action not in action_list_type.__args__:
        action_not_allowed(action)
    
    # парсер альянса
    if entity == "alliance":
        url = f"https://esi.evetech.net/latest/alliances/{entity_id}/?datasource=tranquility"
        if action == "create":
            try:
                Alliances.objects.get(alliance_id=entity_id)
                print(f"Alliance {entity_id} already exists in DB")
                return
            except ObjectDoesNotExist:
                print(f"Start load alliance: {entity_id}")
        resp = GET_request_to_esi(url).json()
        nameicon = load_and_save_icon(entity, entity_id)
        print(f"Successful load alliance: {entity_id}")
        Alliances.objects.update_or_create(
                alliance_id=entity_id,
                defaults={
                    "alliance_id": entity_id,
                    "date_founded": resp.get("date_founded"),
                    "name": resp.get("name"),
                    "ticker": resp.get("ticker"),
                    "response_body": resp,
                    "nameicon": nameicon,
                    }
                )
        print(f"Successful save to DB alliance: {entity_id}")

            
