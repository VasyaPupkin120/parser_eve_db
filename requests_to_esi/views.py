from django.shortcuts import redirect, render
from django.urls import reverse
from requests_to_esi.forms import ParseOneSystemForm
from .services import base_requests, parser_social, parser_types, main_parser
import asyncio

# Create your views here.
def main_request(request):
    return render(request, "requests_to_esi/main_request.html")

def parse_regions(request):
    if request.method == "POST":
        try:
            asyncio.run(main_parser.create_all_entities("only_missing", "region"))
            # asyncio.run(base_parser.create_all_entities("update_all", "region"))
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_regions.html", {"exception": e})
        return redirect(reverse("dbeve_universe:regions"))
    return render(request, "requests_to_esi/parse_regions.html")

def parse_constellations(request):
    if request.method == "POST":
        try:
            asyncio.run(main_parser.create_all_entities("only_missing", "constellation"))
            # asyncio.run(base_parser.create_all_entities("update_all", "constellation"))
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_constellations.html", {"exception": e})
        return redirect(reverse("dbeve_universe:constellations"))
    return render(request, "requests_to_esi/parse_constellations.html")

def parse_systems(request):
    if request.method == "POST":
        try:
            asyncio.run(main_parser.create_all_entities("only_missing", "system"))
            # asyncio.run(base_parser.create_all_entities("update_all", "system"))
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_systems.html", {"exception": e})
        return redirect(reverse("dbeve_universe:systems"))
    return render(request, "requests_to_esi/parse_systems.html")

def parse_one_system(request):
    ...
    # if request.method == "POST":
    #     sys_form = ParseOneSystemForm(request.POST)
    #     if sys_form.is_valid():
    #         system_id = sys_form.cleaned_data["system_id"]
    #     try:
    #         one_entity.create_or_update_one_entity("system", system_id, "update")
    #     except base_requests.StatusCodeNot200Exception as e:
    #         return render(request, "requests_to_esi/parse_one_system.html", {"exception": e})
    #     return redirect(reverse("dbeve_universe:one_system", kwargs={"system_id": system_id}))
    # sys_form = ParseOneSystemForm()
    # context = {"form": sys_form}
    # return render(request, "requests_to_esi/parse_one_system.html", context=context)

def parse_stars(request):
    if request.method == "POST":
        try:
            asyncio.run(main_parser.create_all_entities("only_missing", "star"))
            # asyncio.run(base_parser.create_all_entities("update_all", "star"))
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_stars.html", {"exception": e})
        return redirect(reverse("dbeve_universe:stars"))
    return render(request, "requests_to_esi/parse_stars.html")


def parse_alliances(request):
    async def first_alliance_second_associated_corp():
        """
        Парсинг альянсов состоит из двух частей - парсинг собственно альянсов
        и последующий парсинг списка ассоциированных корпораций этих альянсов.
        
        Ассоциированные корпы надо парсить всегда (параметр update_all) - т.к. 
        они могут вступать в алли и выходить.
        """
        await main_parser.create_all_entities("only_missing", "alliance")
        await main_parser.create_all_entities("update_all", "update_field_id_associated_corporations")
    if request.method == "POST":
        try:
            asyncio.run(first_alliance_second_associated_corp())
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_alliances.html", {"exception": e})
        return redirect(reverse("dbeve_social:all_alliances"))
    return render(request, "requests_to_esi/parse_alliances.html")


def parse_id_associated_corporations(request):
    if request.method == "POST":
        try:
            asyncio.run(main_parser.create_all_entities("update_all", "update_field_id_associated_corporations"))
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/update_field_id_associated_corporations.html", {"exception": e})
        return redirect(reverse("dbeve_social:all_alliances"))
    return render(request, "requests_to_esi/update_field_id_associated_corporations.html")


def parse_corporations(request):
    if request.method == "POST":
        try:
            asyncio.run(main_parser.create_all_entities("only_missing", "corporation"))
        except base_requests.StatusCodeNot200Exception as e:
            return render(request, "requests_to_esi/parse_corporations.html", {"exception": e})
        return redirect(reverse("dbeve_social:all_corporations"))
    return render(request, "requests_to_esi/parse_corporations.html")


