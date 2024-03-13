from typing import Literal
import requests
import time
from django.conf import settings


def entity_not_processed(entity):
    """
    Выброс исключения когда передается сущность, для которой нет логики обработки.
    """
    print(f"\n'{entity}' is not processed\n")
    raise ValueError


def action_not_allowed(action):
    """
    Выброс исключения когда передается действие, которое не может быть применено.
    Т.е. не 'create' или 'upgrade'
    """
    print(f"\n'{action}' is not allowed\n")
    raise ValueError


class StatusCodeNot200Exception(Exception):
    def __init__(self, message, status_code, limit_remain, limit_reset, error_limited, url, resp):
        super().__init__(message)
        self.status_code = status_code
        self.limit_remain = limit_remain
        self.limit_reset = limit_reset
        self.error_limited = error_limited
        self.url = url
        self.resp = resp


def GET_request_to_esi(url):
    """
    Единичный запрос к esi, в случае не 200 ответа необходима нормальная логика обработки

    Может выполняться в два подхода - если в первый раз пришла ошибка, то ожидаем
    конца окна и выполняем повторно запрос. Если во второй запрос также не 200 ответ, то выброс исключения.

    ОЧЕНЬ ВАЖНО - обработка исключения должна происходить на самом верхнем уровне - в контроллере.
    Иначе оно будет перехвачено не там и циклы из предыдущих функций продолжат обращение к esi.

    Логика в приципе позволяет переждать лимит, поэтому исключение должно приводить к остановке всей работы.
    Если оставить обработку где нибудь в функциях систем, то следующим циклом произойдет повтороное обращение
    к GET_request_to_esi и уменьшение счетчика на единицу. То есть блокировка.
    """
    MAX_COUNT_REMAINS = 99
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp

    #FIXME внести сюда обращение к модели-логу для записи всей инфы об неудачном коде. Логирование удачного запроса будет в рабочих функциях - там где запрос вернул результат

    # определяем параметры ошибок
    limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
    limit_reset = resp.headers.get("X-ESI-Error-Limit-Reset")

    # ингда в ответе нет заголовков Remain или Reset, хз почему, но лучше сразу тогда выбросить исключение
    # это бывает когда вылетает 5хх ошибка, например 502
    if not limit_remain or not limit_reset:
        limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
        limit_reset = resp.headers.get("X-ESI-Error-Limit-Reset")
        error_limited = resp.headers.get("X-ESI-Error-Limited")
        error_message = f"Status code: {resp.status_code}\n Limit-Remain: {limit_remain}\n Limit-Reset: {limit_reset}\n Error-Limited:{error_limited}\n URL: {url}\n Response: {resp}" 
        raise StatusCodeNot200Exception(
                error_message,
                status_code=resp.status_code,
                limit_remain=limit_remain,
                limit_reset=limit_reset,
                error_limited=error_limited,
                url=url,
                resp=resp,
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
            resp=resp,
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
        entity_not_processed(entity)

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



