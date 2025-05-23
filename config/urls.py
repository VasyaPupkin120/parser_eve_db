"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from pages.views import index, db_overview
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),

    # приложения-обзорщики БД
    path('dbeve/universe/', include("dbeve_universe.urls", namespace="dbeve_universe")),
    path('dbeve/social/', include("dbeve_social.urls", namespace="dbeve_social")),
    path('dbeve/items/', include("dbeve_items.urls", namespace="dbeve_items")),

    # app requests to esi 
    path("requests_to_esi/", include("requests_to_esi.urls", namespace="requests_to_esi")),

    # app compensation
    path("compensation/", include("compensation.urls", namespace="compensation")),

    # app pages - общие для всех странички
    path('dboverview/', db_overview, name="db_overview"),
    path('', index, name="index"),
]

if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
