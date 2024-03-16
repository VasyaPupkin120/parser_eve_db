from typing import Literal

from django.core.exceptions import ObjectDoesNotExist
from .base_requests import GET_request_to_esi
from dbeve_social.models import Alliances, Corporations

from .one_entity import create_or_update_one_entity


def create_all_alliances():
    """
    """
    url = "https://esi.evetech.net/latest/alliances/?datasource=tranquility"
    alliances_id = GET_request_to_esi(url).json()
    len_alliances = len(alliances_id)
    count = 1
    print("\nSuccessful loading of all alliances id.")
    print("Start downloading information by alliance.")
    for alliance_id in alliances_id:
        print(f"\nLoad: {count}/{len_alliances}")
        create_or_update_one_entity("alliance", alliance_id, "create")
        count += 1

# временная фунцкия-парсер для поиска всех ассоциированных с алли корпороаций.
# def create_only_id_all_associated_corporations():
#     """
#     временная функция для дополнения данных по каждому альянсу списком ассоциированных корп
#     """
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
    corporations_id = []
    for alliance in Alliances.objects.values("response_body"):
        corporations_id.extend(alliance["response_body"]["associated_corp"])
    len_corporations = len(corporations_id)
    count = 1
    print("\nSuccessful compile list all corporations id.")
    print("Start downloading information by all corporation.")
    for corporation_id in corporations_id:
        print(f"\nLoad: {count}/{len_corporations}")
        create_or_update_one_entity("corporation", corporation_id, "create")
        count += 1
