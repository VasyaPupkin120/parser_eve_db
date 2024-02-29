from django.shortcuts import render

def universe(request):
    return render(request, "dbeve_universe/universe.html")

# Create your views here.
def systems_list(request):
    # if not Systems.objects.all():
    #     add_systems_id_in_DB()
    #     systems = Systems.objects.all()
    #     return render(request, "dbeve/systems_id.html", context={"systems": systems, "status": "выполнена загрузка данных из json-файла в БД"})
    # else:
        # systems = Systems.objects.all()
        # return render(request, "dbeve/systems_id.html", context={"systems": systems, "status": "Данные загружены из БД"})
    return render(request, "dbeve_universe/systems.html")

def constellations_list(request):
    return render(request, "dbeve_universe/constellations.html")

def regions_list(request):
    return render(request, "dbeve_universe/regions.html")
