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
    path('load_id_associated_corporations/', load_id_associated_corporations, name="load_id_associated_corporations"),
    path('parse_corporations/', parse_corporations, name="parse_corporations"),
    path('parse_characters/', parse_characters, name="parse_characters"),
    path('load_corporation_history/', load_corporation_history, name="load_corporation_history"),
    path('parse_one_battlereport/', parse_one_battlereport, name="parse_one_battlereport"),

    #dbeve_items
    path('parse_categories/', parse_categories, name="parse_categories"),
    path('parse_groups/', parse_groups, name="parse_groups"),
    path('parse_types/', parse_types, name="parse_types"),
]
