from django.urls import path
from .views import *

app_name = "dbeve_items"

urlpatterns = [
    path('', items, name="items"),
    path('all_categories/', all_categories, name="all_categories"),
    path('all_groups/', all_groups, name="all_groups"),
    path('all_types/', all_types, name="all_types"),
]
