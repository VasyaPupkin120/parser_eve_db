import requests
from .models import ResultJSON
from dbeve_universe.models import *
import pprint
import time

class StatusCodeNot200Exception(Exception):
    def __init__(self, message, status_code, limit_remain, limit_reset, error_limited):
        super().__init__(message)
        self.status_code = status_code
        self.limit_remain = limit_remain
        self.limit_reset = limit_reset
        self.error_limited = error_limited




def request_data_one_system(system_id):
    url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/?datasource=tranquility&language=en"
    response = requests.get(url).json()
    ResultJSON.objects.create(request=url, response=response)

def get_and_save_all_regions():
    """
    Запрашиваем список id регионов, сравниваем с имеющимся списком id регионов в БД,
    если есть новые регионы - добавляем id этого региона в БД. 
        https://esi.evetech.net/latest/universe/regions/?datasource=tranquility

    После чего для  каждого id региона из БД, выполняем функцию для одного региона get_and_save_one_region()
    в который передаем id этого региона
    """
    ...

def get_and_save_one_region(region_id):
    """
    получает id региона, выполняет запрос по этому id, получает от esi список констелляций
        https://esi.evetech.net/latest/universe/regions/10000001/?datasource=tranquility&language=en
    Передает этот список констелляций в get_and_save_all_constellations
    """
    ...

def get_and_save_all_constellations(list_constellatons:list):
    """
    Функция рассчитана на получение  списка id констеллций из - сразу всех или только констелляций одного региона

    Тем или иным образом получили список констелляций, проверяем наличие их в БД, 
    если такой констелляции нет в БД, то добавляем id этой констелляции в БД.
    проходим по списку констелляций и отправляем каждую по очереди в get_and_save_one_constellations

    """
    list_constellatons = list_constellatons[:]
    ...

def get_and_save_one_constellations(constellation_id):
    """
    выполняем запрос инфы по констелляции, получаем список систем. 
        https://esi.evetech.net/latest/universe/constellations/20000012/?datasource=tranquility&language=en
    Этот список систем передаем в функцию get_and_save_systems.
    """
    ...

def get_and_save_systems(list_systems:list):
    """
    функция рассчитана на получение небольшого списка id систем из get_and_save_one_constellations,
    но также можно передать список вообще всех систем, полученный специальным запросом.

    для каждого id из списка проверяем  наличие в БД и если нет - то создаем такую запись.

    после чего для каждого id системы выполняем запрос функции get_and_save_one_system
    """
    list_systems = list_systems[:]
    ...

def get_and_save_one_system(system_id):
    """
    Предполагается что запись об системе с данным id уже есть в БД но 
    неизвестно, есть ли другие данные в этой записи. 

    То есть, нужно определить, полны ли данные об системе, и если это только id,
    то выполняется запрос к esi, иначе запрос не должен выполняться. 

    если в ответе есть группы или типы, то перед занесением инфы в БД по системе 
    нужно создать группу и тип и привязать тип к группе. Полностью парсить все типы 
    не нужно
    """
    system = Systems.objects.get(id=system_id)

    if system.name:
        return "this system has full data"

    url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/?datasource=tranquility&language=en"
    resp = GET_request_to_esi(url)
    print(url)
    print()
    pprint.pprint(resp.status_code)
    print()
    pprint.pprint(resp.headers)
    print()
    print(resp.json())



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
    limit_remain = resp.headers["X-ESI-Error-Limit-Remain"]
    limit_reset = resp.headers["X-ESI-Error-Limit-Reset"]

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
    limit_remain = resp.headers["X-ESI-Error-Limit-Remain"]
    limit_reset = resp.headers["X-ESI-Error-Limit-Reset"]
    error_limited = resp.headers.get("X-ESI-Error-Limited")
    error_message = f"Status code: {resp.status_code}\nLimit-Remain: {limit_remain}\nLimit-Reset: {limit_reset}\nError-Limited:{error_limited}" 
    raise StatusCodeNot200Exception(
            error_message,
            status_code=resp.status_code,
            limit_remain=limit_remain,
            limit_reset=limit_reset,
            error_limited=error_limited,
            )


id_systems = [
    30000001,
    30000002,
    30000003,
    30000004,
    300000040,
    300000050,
    30000006,
    30000007,
    30000008,
    30000009,
    30000010,
]


def test(id_system=None):
    if not id_system:
        # ZS-2LT, для тестов
        url = "https://esi.evetech.net/latest/universe/systems/30004469/?datasource=tranquility&language=en"
    else:
        url = f"https://esi.evetech.net/latest/universe/systems/{id_system}/?datasource=tranquility&language=en"
    resp = GET_request_to_esi(url)
    print(url)
    print()
    pprint.pprint(resp.status_code)
    print()
    pprint.pprint(resp.headers)
    print()
    print(resp.json())

