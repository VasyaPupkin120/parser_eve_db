"""
Синхронные запросы устарели, не использовать в новых функциях-парсерах.
Оставить только в функциях с одним запросом (типа списка альянсов или списка звездных систем).
Остальные фукнции переделать под асинхронные запросы.

"""
from typing import Literal
import requests
import time
from django.conf import settings
from .errors import StatusCodeNot200Exception, raise_entity_not_processed, raise_StatusCodeNot200Exception

import asyncio
import aiohttp
from .asynctimer import async_timed
from typing import List

from . import conf



################################################################################
#                         Блок синхронных запросов.                            #
################################################################################

def GET_request_to_esi(url):
    """
    Единичный синхронный запрос к esi, в случае не 200 ответа необходима нормальная логика обработки

    Может выполняться в два подхода - если в первый раз пришла ошибка, то ожидаем
    конца окна и выполняем повторно запрос. Если во второй запрос также не 200 ответ, то выброс исключения.

    ОЧЕНЬ ВАЖНО - обработка исключения должна происходить на самом верхнем уровне - в контроллере.
    Иначе оно будет перехвачено не там и циклы из предыдущих функций продолжат обращение к esi.

    Логика в приципе позволяет переждать лимит, поэтому исключение должно приводить к остановке всей работы.
    Если оставить обработку где нибудь в функциях систем, то следующим циклом произойдет повтороное обращение
    к GET_request_to_esi и уменьшение счетчика на единицу. То есть блокировка.
    """
    MAX_COUNT_REMAINS = conf.MAX_COUNT_REMAINS
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp

    #FIXME внести сюда обращение к модели-логу для записи всей инфы об неудачном коде. Логирование удачного запроса будет в рабочих функциях - там где запрос вернул результат

    #FIXME на самом деле не нужно выполнять повторный запрос при ответе 404 так как уже точно ничего не поможет

    # определяем параметры ошибок
    limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
    limit_reset = resp.headers.get("X-ESI-Error-Limit-Reset")

    # ингда в ответе нет заголовков Remain или Reset, хз почему, но лучше сразу тогда выбросить исключение
    # это бывает когда вылетает 5хх ошибка, например 502
    if not limit_remain or not limit_reset:
        limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
        limit_reset = resp.headers.get("X-ESI-Error-Limit-Reset")
        error_limited = resp.headers.get("X-ESI-Error-Limited")
        error_message = f"Status code: {resp.status_code}\n Limit-Remain: {limit_remain}\n Limit-Reset: {limit_reset}\n Error-Limited:{error_limited}\n URL: {url}\nFull body response: {resp}\nContent: {resp.content}" 
        raise StatusCodeNot200Exception(
                error_message,
                status_code=resp.status_code,
                limit_remain=limit_remain,
                limit_reset=limit_reset,
                error_limited=error_limited,
                url=url,
                full_body_response=resp,
                content=resp.content
                )

    # нельзя допускать более чем одну ошибку - проще уронить сервис чем возиться с блокировкой ip
    # более чем одна ошибка - это значит где то кривая логика
    if int(limit_remain) < MAX_COUNT_REMAINS:
        exit()

    # ожидание отката окна запроса и повторный запрос
    time.sleep(int(limit_reset) + 10)

    resp = requests.get(url)
    if resp.status_code == 200:
        return resp

    # в случае повторной ошибки - выброс исключения
    limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
    limit_reset = resp.headers.get("X-ESI-Error-Limit-Reset")
    error_limited = resp.headers.get("X-ESI-Error-Limited")
    error_message = f"Status code: {resp.status_code}\nLimit-Remain: {limit_remain}\nLimit-Reset: {limit_reset}\nError-Limited:{error_limited}\nURL: {url}" 
    raise StatusCodeNot200Exception(
            error_message,
            status_code=resp.status_code,
            limit_remain=limit_remain,
            limit_reset=limit_reset,
            error_limited=error_limited,
            url=url,
            full_body_response=resp,
            content=resp.content
            )


###############################################################################
#                           Загрузка изображения.                             #
###############################################################################


def load_and_save_icon(entity: Literal["alliance", "corporation", "character"], entity_id):
    """
    получает название сущности (alliance, corporation, char), id сущности, 
    загружается изображение 128х128 (оно вроде есть и у чаров
    и у корпораций и у алли). 

    Возвращает имя файла изображения (нужно для загрузки из статических файлов,
    т.к. заранее неизвестно какое расширение), его нужно сохранять в модель альянса,
    корпорации и т.д.

    Расширение (jpeg, png) определяется на основе заголовков ответа.

    Нужно помнить, что парсинг изображений идет не с esi а с некоего файлового
    сервера, поэтому нужно как то поаккуратней, там могут быть другие лимиты запросов
    и могут блочить парсинг изображений.
    """

    if entity == "alliance":
        url_images = f"https://images.evetech.net/Alliance/{entity_id}_128.png"
        path = settings.STATICFILES_DIRS[0].joinpath("img/alliances")
    elif entity == "corporation":
        url_images = f"https://images.evetech.net/corporations/{entity_id}/logo?tenant=tranquility&size=128"
        path = settings.STATICFILES_DIRS[0].joinpath("img/corporations")
    elif entity == "character":
        url_images = f"https://images.evetech.net/characters/{entity_id}/portrait?tenant=tranquility&size=128"
        path = settings.STATICFILES_DIRS[0].joinpath("img/characters")
    else:
        raise_entity_not_processed(entity)

    # пробуем использовать ту же функцию загрузки, что и все esi-запросы
    # несмотря на то, что это запрос не к esi а к images.evetech.net
    # в приципе запросы к esi занимают 300-400 мс
    # и на одну сущность - только один запрос изображения,
    # поэтому не буду ставить какие то временные задержки запросов изображений.
    # посмотрим, не будут ли блочить.
    print("start load image")
    resp = GET_request_to_esi(url_images)
    print("succeful load image")

    file_extension = resp.headers["Content-Type"].split("/")[-1]
    filename = f"{entity_id}_128.{file_extension}"
    full_filename = path.joinpath(filename)

    print(f"start save image to {full_filename}")
    with open(full_filename, "wb") as file:
        file.write(resp.content)
    print("succeful save image")

    return filename




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
                # более чем 40 ошибок - это значит где то кривая логика
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
                raise_StatusCodeNot200Exception(url, resp, content)

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
            raise_StatusCodeNot200Exception(url, resp, content)


def get_urls(entity, id_keys):
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
    else:
        raise_entity_not_processed(entity)
    # формируем список кортежей, 0 элемент - url, 1 элемент - id_key
    base = base_url.split("!")
    urls_and_ids = [(base[0] + str(id_key) + base[1], id_key) for id_key in id_keys]
    return urls_and_ids

@async_timed()
async def several_async_requests(session:aiohttp.ClientSession, id_keys:List[str], entity:conf.entity_list_type):
    """
    Принимает сессию, список подставляемых в урл id, сущность, 
    с помощью get_url на основе сущности формирует список урлов для запроса, выполняет запросы,
    возвращает словарь с ключом - id и значением - результатом запроса.
    Обращается к функции-одиночному запросу, получает из нее словарь с результатами
    одного запроса, объединяет все результаты в один возвращаемый словарь.
    Выполняет конкурентные запросы одновременно для всех полученных урл-ов.
    """
    urls_and_ids = get_urls(entity, id_keys)
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
