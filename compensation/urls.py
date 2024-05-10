from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path
from .views import *

app_name = "compensation"
urlpatterns = [
    path('', brs_and_parsing, name="brs_and_parsing"),
    path('markup_battlereport/<str:battlereport_id>/', markup_battlereport, name="markup_battlereport"),
    path('notes_compensations/', notes_compensations, name="notes_compensations"),
    ]
