from aiohttp import ClientSession
import aiohttp
import requests

from .conf import entity_list_type, action_list_type


class StatusCodeNot200Exception(Exception):
    def __init__(self, message, status_code, limit_remain, limit_reset, error_limited, url, resp):
        super().__init__(message)
        self.status_code = status_code
        self.limit_remain = limit_remain
        self.limit_reset = limit_reset
        self.error_limited = error_limited
        self.url = url
        self.resp = resp

def raise_StatusCodeNot200Exception(url:str, resp:aiohttp.ClientResponse|requests.Response):
    """
    Принимает url и результат запроса на этот url, выбрасывает исключение.
    """
    if type(resp) == requests.Response:
        status_code = resp.status_code
    elif type(resp) == aiohttp.ClientResponse:
        status_code = resp.status
    else:
        status_code = 999
    limit_remain = resp.headers.get("X-ESI-Error-Limit-Remain")
    limit_reset = resp.headers.get("X-ESI-Error-Limit-Reset")
    error_limited = resp.headers.get("X-ESI-Error-Limited")
    error_message = f"Status code: {status_code}\nLimit-Remain: {limit_remain}\nLimit-Reset: {limit_reset}\nError-Limited:{error_limited}\nURL: {url}" 
    raise StatusCodeNot200Exception(
            error_message,
            status_code=status_code,
            limit_remain=limit_remain,
            limit_reset=limit_reset,
            error_limited=error_limited,
            url=url,
            resp=resp,
            )

def raise_entity_not_processed(entity):
    """
    Выброс исключения когда передается сущность, для которой нет логики обработки.
    """
    print(f"\n'{entity}' is not processed\n")
    raise ValueError


def raise_action_not_allowed(action):
    """
    Выброс исключения когда передается действие, которое не может быть применено.
    Т.е. не 'create' или 'upgrade'
    """
    print(f"\n'{action}' is not allowed\n")
    raise ValueError


def check_action(action):
    """
    Для ограничения работы исключительно указаными действиями
    """
    if action not in action_list_type.__args__:
        raise_action_not_allowed(action)


def check_entity(entity):
    """
    Для ограничения работы исключительно указаными сущностями.
    """
    if entity not in entity_list_type.__args__:
        raise_entity_not_processed(entity)
