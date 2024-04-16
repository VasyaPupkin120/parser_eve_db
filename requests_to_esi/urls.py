from django.urls import include, path
from .views import *
app_name = "requests_to_esi"
urlpatterns = [
    path('', main_request, name="main_request"),
    # dbeve_universe
    path('parse_regions/', parse_regions, name="parse_regions"),
    path('parse_constellations/', parse_constellations, name="parse_constellations"),
    path('parse_systems/', parse_systems, name="parse_systems"),
    # path('parse_one_system/', parse_one_system, name="parse_one_system"),
    path('parse_stars/', parse_stars, name="parse_stars"),
    
    # dbeve_social
    path('parse_alliances/', parse_alliances, name="parse_alliances"),
    path('parse_id_associated_corporations/', parse_id_associated_corporations, name="parse_id_associated_corporations"),
]
