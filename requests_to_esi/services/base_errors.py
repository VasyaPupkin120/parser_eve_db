class StatusCodeNot200Exception(Exception):
    def __init__(self, message, status_code, limit_remain, limit_reset, error_limited, url, resp):
        super().__init__(message)
        self.status_code = status_code
        self.limit_remain = limit_remain
        self.limit_reset = limit_reset
        self.error_limited = error_limited
        self.url = url
        self.resp = resp


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


