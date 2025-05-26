from celery import Celery
from .testtasks import long_calculations

# Инициализация Celery. Брокер — Redis, бэкенд — Redis (для результатов)
celery_app = Celery(
    'my_tasks',  # Имя приложения
    broker='redis://localhost:6379/0',  # Адрес брокера
    backend='redis://localhost:6379/1'  # Где хранить результаты
)

@celery_app.task
def test(**kwargs):
    return long_calculations(**kwargs)
