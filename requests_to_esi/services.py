import requests
from .models import ResultJSON
import pprint

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


def validate_url(url):
    return True

def GET_request_to_esi(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        limit_remain = resp.headers["X-ESI-Error-Limit-Remain"]
        limit_reset = resp.headers["X-ESI-Error-Limit-Reset"]
        error_limited = resp.headers.get("X-ESI-Error-Limited")
        error_message = f"Status code: {resp.status_code}\nLimit-Remain: {limit_remain}\nLimit-Reset: {limit_reset}\nError-Limited:{error_limited}", 
        raise StatusCodeNot200Exception(
                error_message,
                status_code=resp.status_code,
                limit_remain=limit_remain,
                limit_reset=limit_reset,
                error_limited=error_limited,
                )
    return resp

def parser_all_systems():
    MAX_COUNT_REMAINS = 98
    urls = []
    for id_system in id_systems:
        url = f"https://esi.evetech.net/latest/universe/systems/{id_system}/?datasource=tranquility&language=en"
        urls.append(url)
    for url in urls:
        try:
            resp = GET_request_to_esi(url)
        except StatusCodeNot200Exception as e:
            if e.status_code == 420:
                return 420
            elif e.status_code == 404 and int(e.limit_remain) > MAX_COUNT_REMAINS:
                continue
            else:
                print("\n\nSOME EXCEPTION IN 'PARSER_ALL_SYSTEMS'\n\n")
                return -1
        print(url)
        print()
        pprint.pprint(resp.status_code)
        print()
        pprint.pprint(resp.headers)
        print()
        print(resp.json())






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

