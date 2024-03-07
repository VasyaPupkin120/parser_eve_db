from django.urls import include, path
from .views import *
app_name = "requests_to_esi"
urlpatterns = [
    path('', main_request, name="main_request"),
    path('parse_regions/', parse_regions, name="parse_regions"),
    path('parse_constellations/', parse_constellatons, name="parse_constellations"),
    path('get_one_system/', get_one_system, name="get_one_system"),
    path('all_lines/', all_lines, name="all_lines"),
]
