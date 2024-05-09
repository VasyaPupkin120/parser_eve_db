from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path
from .views import *

app_name = "compensation"
urlpatterns = [
    path('', brs_and_parsing, name="brs_and_parsing"),
    path('br_for_compense/<str:battlereport_id>/', br_for_compense, name="br_for_compense"),
    ]
