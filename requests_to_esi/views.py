from django.shortcuts import redirect, render
from django.urls import reverse
from .models import ResultJSON
from requests_to_esi.forms import RequestSystemForm
from .services.base_requests import request_data_one_system, StatusCodeNot200Exception
from .services.universe import get_and_save_all_regions, get_and_save_all_constellations

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
            get_and_save_all_regions(action="update")
        except StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_regions.html", {"exception": e})
        return redirect(reverse("dbeve_universe:regions"))
    return render(request, "requests_to_esi/parse_regions.html")

def parse_constellatons(request):
    if request.method == "POST":
        try:
            get_and_save_all_constellations(action="update")
        except StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_constellations.html", {"exception": e})
        return redirect(reverse("dbeve_universe:constellations"))
    return render(request, "requests_to_esi/parse_constellations.html")
