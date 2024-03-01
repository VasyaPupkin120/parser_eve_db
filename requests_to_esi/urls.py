from django.urls import include, path
from .views import *
app_name = "requests_to_esi"
urlpatterns = [
    path('', main_request, name="main_request"),
]
