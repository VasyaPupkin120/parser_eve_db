from celery import Celery, shared_task
from .testtasks import long_calculations
# from .parser.parser_main import create_all_entities

# Инициализация Celery. Брокер — Redis, бэкенд — Redis (для результатов)
# celery_app = Celery(
#     'config',  # Имя приложения-проекта, в котором хранятся настройки уровня проекта
#     broker='redis://localhost:6379/0',  # Адрес брокера
#     backend='redis://localhost:6379/1'  # Где хранить результаты
# )

# @celery_app.task
@shared_task
def test(**kwargs):
    return long_calculations(**kwargs)


# @celery_app.task
# @shared_task
# def parser(*args, **kwargs):
#     return create_all_entities(*args, **kwargs)
