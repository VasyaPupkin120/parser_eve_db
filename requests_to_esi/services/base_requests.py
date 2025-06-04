"""
Синхронные запросы устарели, не использовать в новых функциях-парсерах.
Оставить только в функциях с одним запросом (типа списка альянсов или списка звездных систем).
Остальные фукнции переделать под асинхронные запросы.

"""
from asgiref.sync import sync_to_async


from typing import Literal
import requests
import time
from django.conf import settings

from dbeve_social.models import Killmails

from . import errors
from .errors import StatusCodeNot200Exception, raise_entity_not_processed, raise_StatusCodeNot200Exception

import asyncio
import aiohttp
from .asynctimer import async_timed
from typing import List

from . import conf
from .conf import entity_list_type



################################################################################
#                         Блок синхронных запросов.                            #
################################################################################
def GET_request_to_esi(url):
    """
    Единичный синхронный запрос к esi, в случае не 200 ответа сразу выброс исключения - 
    это разовые запросы, 500е ошибки крайне маловероятны, и можно будет при нужде
    запустить заново.
    """
    #FIXME внести сюда обращение к модели-логу для записи всей инфы об неудачном коде. Логирование удачного запроса будет в рабочих функциях - та где запрос вернул результат
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp
    else:
        raise_StatusCodeNot200Exception(url, resp)


################################################################################
#                         Блок aсинхронных запросов.                            #
################################################################################

@async_timed()
async def async_GET_requrest_to_esi(session: aiohttp.ClientSession, url: str, id_key: int):
    """
    Принимает сеанс, url, ключ - чтобы проще было идентифицировать запрос 
    в условиях асинхронности и отсутствия сохранения порядка запросов.
    Повторный запрос только в случае 500х ошибок - в надежде на то что сервер поднялся.
    Логика защиты от ошибочных запросов должна быть выше по вызовам - т.к. 
    асинхронно в текущем запросе не получится остановить выполнение остальных запросов.
    """
    MAX_COUNT_REMAINS = conf.MAX_COUNT_REMAINS
    async with session.get(url) as resp:
        content = await resp.json()
        if resp.status == 200:
            return {id_key: content}
        else:
            print("Error request.")
            print(f"Error url: {url}")
            # возможны два варианта ошибок 404 - либо ошибочный url, либо персонаж удален
            # нужно различать на основе содержимого ответа. Для удаленных персонажей исклюение
            # не выбрасывается, просто выполняется ожидание без последующего повторного запроса.
            # если ошибка в запросе, то нет смысла в повторном запросе
            # поэтому сразу формируем и выбрасываем исключение
            if resp.status not in [500, 501, 502, 503, 504, 505]:

                # нельзя допускать слишком много ошибок - проще уронить сервис чем возиться с блокировкой ip
                # если почему то нет параметра X-ESI-Error-Limit-Remain - счетчика ошибок, то тоже надо ронять
                limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
                if not limit_remain or int(limit_remain) < MAX_COUNT_REMAINS:
                    print(f"TOO MANY ERRORS! X-ESI-Error-Limit-Remain: {limit_remain}. PARSER TERMINATED!")
                    exit()

                if content["error"] == "Character has been deleted!":
                    print("This error is caused by a request for information on a deleted character..")
                    # запуск ожидания отката окна не на каждой ошибке а скажем если ошибок совершено не более чем 20 
                    if int(limit_remain) < 80:
                        print("Wait until the error timer is cleared.")
                        await asyncio.sleep(conf.TIME_WAIT_NEXT_REQUEST)
                    else:
                        print("Information about this has been sent to the database. The error limit has not been exceeded, the next request will be executed.")
                    return {id_key: {"is_deleted": True}}
                # для случаев когда такой странички не существует - просто выброс исключения.
                raise_StatusCodeNot200Exception(url, resp)

    # повторный запрос только в случае ошибок сервера
    # ожидание отката окна запроса с небольшим запасом и повторный запрос
    # ожидание должно быть асинхронным  но не таской, т.е. asyncio.sleep без оборачивания таской
    # - чтобы оно блокировало исключительно ту корутину в которой выполняется 
    # текущий запрос. 
    #FIXME Иногда бывает, что 500ошибка на запрос удаленного чара - тогда выполняется повторный запрос этого чара.
    print("Повторный запрос")
    await asyncio.sleep(conf.TIME_WAIT_NEXT_REQUEST)
    async with session.get(url) as resp:
        content = await resp.json()
        if resp.status == 200:
            # return {id_key: {"headers": resp.headers, "content": await resp.json()}}
            return {id_key: content}
        else:
            # в случае повторной ошибки - выброс исключения
            raise_StatusCodeNot200Exception(url, resp)


@sync_to_async
def killmail_esi_urls(id_keys):
    """
    Формирует список url для запроса к esi - запрашивает в БД
    хэш киллмыл и формирует url.  Предполагается что хэш каким то образом уже получен.
    Отдельная функция - т.к. url у киллмыла формируется из двух 
    изменяющихся частей а get_url работает с url-ами у которых 
    только один изменяющийся параметр.
    """
    urls_and_ids = []
    killmails = Killmails.objects.filter(killmail_id__in=id_keys).values("killmail_id", "killmail_hash")
    for killmail in killmails:
        killmail_id = killmail["killmail_id"]
        killmail_hash = killmail["killmail_hash"]
        url = f"https://esi.evetech.net/latest/killmails/{killmail_id}/{killmail_hash}/?datasource=tranquility"
        urls_and_ids.append((url, killmail_id))
    return urls_and_ids


async def get_urls(entity, id_keys):
    """
    Принимает сущность и набор id, формирует урлы для запросов в esi.
    """
    if entity == "region":
        base_url = "https://esi.evetech.net/latest/universe/regions/!/?datasource=tranquility&language=en"
    elif entity == "constellation":
        base_url = "https://esi.evetech.net/latest/universe/constellations/!/?datasource=tranquility&language=en"
    elif entity == "system":
        base_url = "https://esi.evetech.net/latest/universe/systems/!/?datasource=tranquility&language=en"
    elif entity == "star":
        base_url = "https://esi.evetech.net/latest/universe/stars/!/?datasource=tranquility"
    elif entity == "alliance":
        base_url = "https://esi.evetech.net/latest/alliances/!/?datasource=tranquility"
    elif entity == "load_id_associated_corporations":
        base_url = "https://esi.evetech.net/latest/alliances/!/corporations/?datasource=tranquility"
    elif entity == "corporation":
        base_url = "https://esi.evetech.net/latest/corporations/!/?datasource=tranquility"
    elif entity == "character":
        base_url = "https://esi.evetech.net/latest/characters/!/?datasource=tranquility"
    elif entity == "load_corporation_history":
        base_url = "https://esi.evetech.net/latest/characters/!/corporationhistory/?datasource=tranquility"
    elif entity == "category":
        base_url = "https://esi.evetech.net/latest/universe/categories/!/?datasource=tranquility&language=en"
    elif entity == "group":
        base_url = "https://esi.evetech.net/latest/universe/groups/!/?datasource=tranquility&language=en"
    elif entity == "type":
        base_url = "https://esi.evetech.net/latest/universe/types/!/?datasource=tranquility&language=en"
    elif entity == "killmail_from_esi":
        urls = await killmail_esi_urls(id_keys)
        return urls
    else:
        raise_entity_not_processed(entity)
    # формируем список кортежей, 0 элемент - url, 1 элемент - id_key
    base = base_url.split("!")
    urls_and_ids = [(base[0] + str(id_key) + base[1], id_key) for id_key in id_keys if id_key != 0]
    return urls_and_ids

@async_timed()
async def several_async_requests(
        session:aiohttp.ClientSession,
        id_keys:List[str],
        entity:conf.entity_list_type,
        ):
    """
    Принимает сессию, список подставляемых в урл id, сущность, 
    с помощью get_url на основе сущности формирует список урлов для запроса, выполняет запросы,
    возвращает словарь с ключом - id и значением - результатом запроса.
    Обращается к функции-одиночному запросу, получает из нее словарь с результатами
    одного запроса, объединяет все результаты в один возвращаемый словарь.
    Выполняет конкурентные запросы одновременно для всех полученных урл-ов.

    для некоторых сущностей недостаточно id и нужны еще параметры, например для killmaill_esi.
    """
    # внутри urls_and_ids есть запросы в БД, нужно сделать эту функцию асинхронной 
    # чтобы внутри можно было вызывать sync_to_async функции. Криво, но пофиг.
    urls_and_ids = await get_urls(entity, id_keys)
    out_responses = {}
    pending = []
    for url, id_key in urls_and_ids:
        pending.append(asyncio.create_task(async_GET_requrest_to_esi(session, url, id_key)))
    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_EXCEPTION)
        # обход завершившихся задач, обработка исключения
        for done_task in done:
            # если не исключение - дополняем словарь с данными для ответа
            if done_task.exception() is None:
                out_responses.update(done_task.result())
            # если исключение - то отчет, снятие всех остальных задач и выброс исключения
            else:
                print("Исключение: ", done_task)
                print("Возникло исключение. Запуск снятия остальных задач.")
                for pending_task in pending:
                    pending_task.cancel()
                print("Задачи сняты. Запуск выброса исключения.")
                await done_task
    return out_responses
