from django.shortcuts import render
from .models import *

def universe(request):
    return render(request, "dbeve_universe/universe.html")

# Create your views here.
def systems_list(request):
    if not Systems.objects.all():
        return render(request, "dbeve_universe/systems.html", context={"status": "отсутствуют данные в БД"})
    else:
        systems = Systems.objects.all()
        return render(request, "dbeve_universe/systems.html", context={"systems": systems, "status": "Данные загружены из БД"})

def constellations_list(request):
    if not Constellations.objects.all():
        return render(request, "dbeve_universe/constellations.html", context={"status": "отсутствуют данные в БД"})
    else:
        constellations =  Constellations.objects.all()
        return render(request, "dbeve_universe/constellations.html", context={"constellations": constellations, "status": "Данные загружены из БД"})

def regions_list(request):
    if not Regions.objects.all():
        return render(request, "dbeve_universe/regions.html", context={"status": "отсутствуют данные в БД"})
    else:
        systems =  Regions.objects.all()
        return render(request, "dbeve_universe/regions.html", context={"regions": systems, "status": "Данные загружены из БД"})
