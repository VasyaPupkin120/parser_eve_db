from django.shortcuts import render
from .models import *

def universe(request):
    return render(request, "dbeve_universe/universe.html")

# Create your views here.
def regions_list(request):
    if not Regions.objects.all():
        return render(request, "dbeve_universe/regions.html", context={"status": "отсутствуют данные в БД"})
    else:
        regions =  Regions.objects.all()
        return render(request, "dbeve_universe/regions.html", context={"regions": regions, "status": "Данные загружены из БД"})

def constellations_list(request):
    if not Constellations.objects.all():
        return render(request, "dbeve_universe/constellations.html", context={"status": "отсутствуют данные в БД"})
    else:
        constellations =  Constellations.objects.all()
        return render(request, "dbeve_universe/constellations.html", context={"constellations": constellations, "status": "Данные загружены из БД"})

def systems_list(request):
    if not Systems.objects.all():
        return render(request, "dbeve_universe/systems.html", context={"status": "отсутствуют данные в БД"})
    else:
        systems = Systems.objects.all()
        return render(request, "dbeve_universe/systems.html", context={"systems": systems, "status": "Данные загружены из БД"})

def stars_list(request):
    if not Stars.objects.all():
        return render(request, "dbeve_universe/stars.html", context={"status": "отсутствуют данные в БД"})
    else:
        stars =  Stars.objects.all()
        return render(request, "dbeve_universe/stars.html", context={"stars": stars, "status": "Данные загружены из БД"})
