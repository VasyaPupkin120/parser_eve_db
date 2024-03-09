from django.shortcuts import redirect, render
from django.urls import reverse
from .models import ResultJSON
from requests_to_esi.forms import RequestSystemForm
from .services.base_requests import request_data_one_system, StatusCodeNot200Exception
from .services.universe import *

# Create your views here.
def main_request(request):
    return render(request, "requests_to_esi/main_request.html")

def get_one_system(request):
    if request.method == "POST":
        sys_form = RequestSystemForm(request.POST)
        if sys_form.is_valid():
            system_id = sys_form.cleaned_data["system_id"]
            request_data_one_system(system_id)
            # очищаем форму
            sys_form = RequestSystemForm()
            return render(request, "requests_to_esi/request_one_system.html", context={"form": sys_form})

    else:
        sys_form = RequestSystemForm()
    context = {"form": sys_form}
    return render(request, "requests_to_esi/request_one_system.html", context=context)


def all_lines(request):
    data = ResultJSON.objects.all()
    return render(request, "requests_to_esi/all_lines.html", context={"data": data})


def parse_regions(request):
    if request.method == "POST":
        try:
            create_all_regions()
        except StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_regions.html", {"exception": e})
        return redirect(reverse("dbeve_universe:regions"))
    return render(request, "requests_to_esi/parse_regions.html")

def parse_constellatons(request):
    if request.method == "POST":
        try:
            create_all_constellations()
        except StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_constellations.html", {"exception": e})
        return redirect(reverse("dbeve_universe:constellations"))
    return render(request, "requests_to_esi/parse_constellations.html")

def parse_systems(request):
    if request.method == "POST":
        try:
            create_all_systems()
        except StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_systems.html", {"exception": e})
        return redirect(reverse("dbeve_universe:systems"))
    return render(request, "requests_to_esi/parse_systems.html")

def parse_stars(request):
    if request.method == "POST":
        try:
            create_all_stars()
        except StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_stars.html", {"exception": e})
        return redirect(reverse("dbeve_universe:stars"))
    return render(request, "requests_to_esi/parse_stars.html")
