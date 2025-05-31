import time
from dbeve_universe.models import Regions
from celery import shared_task

@shared_task
def test_task():
    time.sleep(10)
    print(Regions.objects.all())
