import time
import asyncio
from celery import shared_task
from django.shortcuts import render
from .services import parser_main, base_requests


@shared_task
def test_task():
    time.sleep(10)
    print("test task: wait 10 sec")


@shared_task
def parse(*args, **kwargs):
    try:
        asyncio.run(parser_main.create_all_entities(*args, **kwargs))
        return "success"
    except base_requests.StatusCodeNot200Exception as e:
        return str(e)
