import os
import time
from celery import Celery
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings")
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()


@app.task
def debug_task():
    time.sleep(20)
    print("hello from debug task")


@app.task
def print_reg():
    time.sleep(5)
    from dbeve_universe.models import Regions
    print(Regions.objects.all())

