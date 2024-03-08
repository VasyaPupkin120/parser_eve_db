from django.urls import include, path
from .views import *
app_name = "dbeve_universe"
urlpatterns = [
    path('', universe, name="universe"),
    path('regions/', regions_list, name="regions"),
    path('constellations/', constellations_list, name="constellations"),
    path('systems/', systems_list, name="systems"),
    path('stars/', stars_list, name="stars"),
]
