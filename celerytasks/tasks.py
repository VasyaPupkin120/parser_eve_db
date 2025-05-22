from celery import Celery
import time

# Инициализация Celery. Брокер — Redis, бэкенд — Redis (для результатов)
celery_app = Celery(
    'my_tasks',  # Имя приложения
    broker='redis://localhost:6379/0',  # Адрес брокера
    backend='redis://localhost:6379/0'  # Где хранить результаты
)

# Простая задача
@celery_app.task
def add(x, y):
    time.sleep(3)  # Задержка 3 секунд
    return x + y

# Долгая задача (имитация)
@celery_app.task
def process_data(data):
    time.sleep(13)  # Задержка 13 секунд
    return f"Processed: {data.upper()}"
