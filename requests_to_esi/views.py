from django.shortcuts import redirect, render
from django.urls import reverse
from requests_to_esi.forms import ParseOneSystemForm
from .services import base_requests, one_entity, social, types, universe

# Create your views here.
def main_request(request):
    return render(request, "requests_to_esi/main_request.html")

def parse_regions(request):
    if request.method == "POST":
        try:
            universe.create_all_regions()
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_regions.html", {"exception": e})
        return redirect(reverse("dbeve_universe:regions"))
    return render(request, "requests_to_esi/parse_regions.html")

def parse_constellatons(request):
    if request.method == "POST":
        try:
            universe.create_all_constellations()
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_constellations.html", {"exception": e})
        return redirect(reverse("dbeve_universe:constellations"))
    return render(request, "requests_to_esi/parse_constellations.html")

def parse_systems(request):
    if request.method == "POST":
        try:
            universe.create_all_systems()
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_systems.html", {"exception": e})
        return redirect(reverse("dbeve_universe:systems"))
    return render(request, "requests_to_esi/parse_systems.html")

def parse_one_system(request):
    if request.method == "POST":
        sys_form = ParseOneSystemForm(request.POST)
        if sys_form.is_valid():
            system_id = sys_form.cleaned_data["system_id"]
        try:
            one_entity.create_or_update_one_entity("system", system_id, "update")
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_one_system.html", {"exception": e})
        return redirect(reverse("dbeve_universe:one_system", kwargs={"system_id": system_id}))
    sys_form = ParseOneSystemForm()
    context = {"form": sys_form}
    return render(request, "requests_to_esi/parse_one_system.html", context=context)

def parse_stars(request):
    if request.method == "POST":
        try:
            universe.create_all_stars()
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_stars.html", {"exception": e})
        return redirect(reverse("dbeve_universe:stars"))
    return render(request, "requests_to_esi/parse_stars.html")

def parse_alliances(request):
    if request.method == "POST":
        try:
            social.create_all_alliances()
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_alliances.html", {"exception": e})
        return redirect(reverse("dbeve_social:alliances"))
    return render(request, "requests_to_esi/parse_alliances.html")


def parse_associated_corporations(request):
    if request.method == "POST":
        try:
            social.create_all_associated_corporations()
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_associated_corporations.html", {"exception": e})
        return redirect(reverse("dbeve_social:all_corporations"))
    return render(request, "requests_to_esi/parse_associated_corporations.html")
