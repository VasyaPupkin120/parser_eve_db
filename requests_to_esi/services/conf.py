"""
Некоторые общие данные для всех модулей.
"""

from typing import Literal

# запас по ошибкам - для сравнения с параметром X-ESI-Error-Limit-Remain
MAX_COUNT_REMAINS = 70

# время ожидания для повторного запроса после 500х результатов
# 70 - стандартное время окна + 10 секунд на запас
# попробовал 10 секунд - не хватает этого времени - повторная 500я ошибка
TIME_WAIT_NEXT_REQUEST = 70

# общее количество конкурентных запросов.
# почему то если 15 и более - чет подвисает вычисление, хз где, на моей стороне или стороне сервера
# оставлю максимум 10 конкурентных запросов
# если больше - то почему то первый чанк отрабатывает нормально, а второй и остальные - нет
# пока оставлю 10
NUMBER_OF_REQUEST = 10

# типы начинающиеся с load - типы не для полноценной записи в БД а для обновления какого либо поля
action_list_type = Literal["only_missing", "update_all", "linking"]
entity_list_type = Literal[
        "region",
        "constellation",
        "system",
        "star",
        "alliance",
        "load_id_associated_corporations",
        "corporation",
        "character",
        "load_corporation_history",
        "category",
        "group",
        "type",
        "battlereport",
        "killmail_from_esi",
        "killmail_from_br",
        "victim", 
        "attacker",
        ] 
