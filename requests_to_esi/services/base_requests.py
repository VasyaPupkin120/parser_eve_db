import requests
import time

class StatusCodeNot200Exception(Exception):
    def __init__(self, message, status_code, limit_remain, limit_reset, error_limited, url, resp):
        super().__init__(message)
        self.status_code = status_code
        self.limit_remain = limit_remain
        self.limit_reset = limit_reset
        self.error_limited = error_limited
        self.url = url
        self.resp = resp

def request_data_one_system(system_id):
    url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/?datasource=tranquility&language=en"
    response = requests.get(url).json()


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
