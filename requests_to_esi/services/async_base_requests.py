import asyncio
import aiohttp
from .asynctimer import async_timed
from .base_errors import StatusCodeNot200Exception, raise_StatusCodeNot200Exception
from typing import List

@async_timed()
async def async_GET(session: aiohttp.ClientSession, url: str, id_key: int):
    """
    Принимает сеанс, url, ключ - чтобы проще было идентифицировать запрос 
    в условиях асинхронности и отсутствия сохранения порядка запросов.
    Повторный запрос только в случае 500х ошибок - в надежде на то что сервер поднялся.
    Логика защиты от ошибочных запросов должна быть выше по вызовам - т.к. 
    асинхронно в текущем запросе не получится остановить выполнение остальных запросов.
    """
    MAX_COUNT_REMAINS = 90
    async with session.get(url) as resp:
        if resp.status == 200:
            # попробуем возвращать просто результат, без заголовков
            # return {id_key: {"headers": resp.headers, "content": await resp.json()}}
            return {id_key: await resp.json()}
        else:
            print("Ошибка запроса")
            # нельзя допускать слишком много ошибок - проще уронить сервис чем возиться с блокировкой ip
            # более чем 40 ошибок - это значит где то кривая логика
            # если почему то нет параметра limit_remain то тоже надо ронять
            limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
            if not limit_remain or int(limit_remain) < MAX_COUNT_REMAINS:
                print("ERRORS. TERMINATE.")
                exit()
            # если ошибка в запросе, то нет смысла в повторном запросе
            # поэтому сразу формируем и выбрасываем исключение
            if resp.status not in [500, 501, 502, 503, 504, 505]:
                raise_StatusCodeNot200Exception(url, resp)

    # повторный запрос только в случае ошибок сервера
    # ожидание отката окна запроса с небольшим запасом и повторный запрос
    # ожидание должно быть асинхронным  но не таской, т.е. asyncio.sleep без оборачивания таской
    # - чтобы оно блокировало исключительно ту корутину в которой выполняется 
    # текущий запрос
    print("Повторный запрос")
    await asyncio.sleep(70)
    async with session.get(url) as resp:
        if resp.status == 200:
            # return {id_key: {"headers": resp.headers, "content": await resp.json()}}
            return {id_key: await resp.json()}
        else:
            # в случае повторной ошибки - выброс исключения
            raise_StatusCodeNot200Exception(url, resp)


@async_timed()
async def several_async_requests(session:aiohttp.ClientSession, base_url:str, id_keys:List[str]):
    """
    Принимает сессию, базовый урл, список подставляемых в урл id, 
    формирует список урлов для запроса, выполняет запросы,
    возвращает словарь с ключом - id и значением - результатом запроса.
    Обращается к функции-одиночному запросу, получает из нее словарь с результатами
    одного запроса, объединяет все результаты в один возвращаемый словарь.
    Выполняет конкурентные запросы одновременно для всех полученных урл-ов.

    Использует ! как символ, вместо которого должен вставляться id.
    
    """
    # формируем список кортежей, 0 элемент - url, 1 элемент - id_key
    base = base_url.split("!")
    list_urls = [(base[0] + str(id_key) + base[1], id_key) for id_key in id_keys]
    out_responses = {}
    pending = []
    for url, id_key in list_urls:
        pending.append(asyncio.create_task(async_GET(session, url, id_key)))
    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_EXCEPTION)
        # обход завершившихся задач, обработка исключения
        for done_task in done:
            # если не исключение - дополняем словарь с данными для ответа
            if done_task.exception() is None:
                out_responses.update(done_task.result())
            # если исключение - то отчет, снятие всех остальных задач
            else:
                print("Возникло исключение")
                for pending_task in pending:
                    pending_task.cancel()
    return out_responses

async def reqeust_some_alliance():
    base_url = "https://esi.evetech.net/latest/alliances/!/?datasource=tranquility"
    id_keys = [
            99012122,
            99011387,
            # 99031,
            # 99041,
            1900696668,
            99003581,
            99000006,
            99000008,
            99000026,
            99000036,
            99000063,
            99000068,
            99000069,
            99000083,
            99000102,
            99000103,
            99000112,
            99000116,
            99000129,
            99000137,
            99000138,
            99000140,
            99000152,
            99000153,
            99000156,
            99000163,
            99000174,
            99000180,
            99000182,
            99000200,
            99000203,
            99000211,
            99000224,
            99000231,
            99000236,
            99000239,
            99000253,
            99000267,
            99000276,
            99000277,
            99000281,
            99000282,
            99000285,
            99000289,
            99000293,
            99000295,
            99000314,
            99000316,
            99000343,
            99000344,
            99000353,
            99000355,
            99000385,
            99000397,
            99000403,
            99000409,
            99000410,
            99000423,
            99000429,
            99000433,
            99000448,
            99000456,
            99000459,
            99000466,
            99000469,
            99000476,
            99000477,
            99000481,
            99000484,
            99000498,
            99000510,
            99000519,
            99000526,
            99000531,
            99000540,
            99000553,
            99000580,
            99000586,
            99000598,
            99000604,
            99000608,
            99000609,
            99000610,
            99000620,
            99000631,
            99000637,
            99000645,
            99000652,
            99000661,
            99000693,
            99000714,
            99000724,
            99000726,
            99000733,
            99000739,
            99000756,
            99000765,
            99000767,
            99000770,
            99000796,
            99000813,
            99000814,
            99000818,
            99000819,
            99000827,
            99000828,
            99000833,
            99000846,
            99000850,
            99000852,
            99000854,
            99000866,
                 ]

    async with aiohttp.ClientSession() as session:
        responses = await several_requests(session, base_url, id_keys)
    import pprint
    pprint.pprint(responses)


if __name__ == "__main__":
    asyncio.run(reqeust_some_alliance())
    
