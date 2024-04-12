"""
Некоторые общие данные для всех модулей.
"""

from typing import Literal

# общее количество конкурентных запросов.
# почему то если 15 и более - чет подвисает вычисление, хз где, на моей стороне или стороне сервера
# оставлю максимум 10 конкурентных запросов
# если больше - то почему то первый чанк отрабатывает нормально, а второй и остальные - нет
# пока оставлю 10
NUMBER_OF_REQUEST = 10

action_list_type = Literal["add_missing", "update_all"]
entity_list_type = Literal["region", "constellation", "system", "star", "alliance", "corporation", "character"] 
