from django.conf import settings
from django.conf.urls.static import static

from django.urls import include, path
from .views import *

app_name = "dbeve_social"
urlpatterns = [
    path('', social, name="social"),
    path('one_alliance/<int:alliance_id>/', one_alliance, name="one_alliance"),
    path('all_alliances/', all_alliances, name="all_alliances"),
    path('all_corporations/', all_corporations, name="all_corporations"),
    path('all_characters/', all_characters, name="all_characters"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
