from typing import Literal

from django.core.exceptions import ObjectDoesNotExist
from .base_requests import GET_request_to_esi
from dbeve_social.models import Alliances, Corporations

from .enter_entitys_to_db import enter_entitys_to_db


# временная фунцкия-парсер для поиска всех ассоциированных с алли корпороаций.
def create_only_id_all_associated_corporations():
    """
    временная функция для дополнения данных по каждому альянсу списком ассоциированных корп
    """
    ...
#     from .one_entity import get_associated_corp
#     alliances = Alliances.objects.all()
#     count = 1
#     len_alliaces = len(alliances)
#     for alliance in alliances:
#         print(f"{count}/{len_alliaces}")
#         print(f"внесение списка корпроаций в альянс {alliance.alliance_id}")
#         if alliance.response_body.get("associated_corp"):
#             # если этот список уже заполнен, то не нужно выполнять запрос для его создания
#             print(f"альянс {alliance.alliance_id} уже содержит список связанных корпораций")
#             count += 1
#             continue
#         associated_corporatons = get_associated_corp(
#                 alliance.alliance_id,
#                 alliance.response_body.get("creator_corporation_id"),
#                 alliance.response_body.get("executor_corporation_id")
#             )
#         
#         resp_body = alliance.response_body
#         resp_body["associated_corp"] = associated_corporatons
#         alliance.response_body = resp_body
#         alliance.save()
#         # alliance.response_body = resp_body
#         print(f"успешно выполнено внесение списка корпораций в альянс {alliance.alliance_id}")
#         count += 1

def create_all_associated_corporations():
    """
    Запрашивает в БД у альянсов списки id ассоциированных корпораций,
    объединяет их в один большой список, запрашивает инфу для каждой.
    """
    ...
    # corporations_id = []
    # for alliance in Alliances.objects.values("response_body"):
    #     corporations_id.extend(alliance["response_body"]["associated_corp"])
    # len_corporations = len(corporations_id)
    # count = 1
    # print("\nSuccessful compile list all corporations id.")
    # print("Start downloading information by all corporation.")
    # for corporation_id in corporations_id:
    #     print(f"\nLoad: {count}/{len_corporations}")
    #     create_or_update_one_entity("corporation", corporation_id, "create")
        # count += 1


def create_all_associated_characters():
    """
    Запрашивает в БД чары, ассоциированные с альянсами и корпами - 
    т.е. ceo корпорации, creator корпорации, creator альянса, объединяет их 
    в список, запрашивает в esi инфу по каждому.
    """
    ...
    # characters_id = []
    # for alliance in Alliances.objects.values("response_body"):
    #     characters_id.append(alliance["response_body"]["creator_id"])
    # for corporation in Corporations.objects.values("response_body"):
    #     characters_id.append(corporation["response_body"]["creator_id"])
    #     characters_id.append(corporation["response_body"]["ceo_id"])
    # characters_id = set(characters_id)
    # print(len(characters_id))
    # if 90238191 in characters_id:
    #     print("90238191")
