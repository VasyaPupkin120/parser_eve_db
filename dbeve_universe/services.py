import requests
import json
from .models import Systems, Constellations, Regions

# def get_systems_to_json_file():
#     url = "https://esi.evetech.net/latest/universe/systems/?datasource=tranquility"
#     response = requests.get(url)
#     with open('dbeve_universe/jsons/systems.json', "w") as file:
#         json.dump(
#                 response.json(),
#                 file,
#                 ensure_ascii=False,
#                 indent=4,
#                   )
#     return response

# def get_regions_to_json_file():
#     url = "https://esi.evetech.net/latest/universe/regions/?datasource=tranquility"
#     response = requests.get(url)
#     with open('dbeve_universe/jsons/regions.json', "w") as file:
#         json.dump(
#                 response.json(),
#                 file,
#                 ensure_ascii=False,
#                 indent=4,
#                   )
#     return response
#
# def get_constellations_to_json_file():
#     url = "https://esi.evetech.net/latest/universe/constellations/?datasource=tranquility"
#     response = requests.get(url)
#     with open('dbeve_universe/jsons/constellations.json', "w") as file:
#         json.dump(
#                 response.json(),
#                 file,
#                 ensure_ascii=False,
#                 indent=4,
#                   )
#     return response




# def add_systems_id_in_DB(systems):
#     for system_id in systems:
#         Systems.objects.create(system_id=system_id)
#
# def add_constellations_id_in_DB(constellations):
#     for constellation_id in constellations:
#         Constellations.objects.create(constellation_id=constellation_id)
#
# def add_regions_id_in_DB(regions):
#     for region_id in regions:
#         Regions.objects.create(region_id=region_id)
#
# namefiles = ["systems", "constellations", "regions"]
#
# def get_from_json_file():
#     out_d = {}
#     for namefile in namefiles:
#         with open(f'/code/dbeve_universe/jsons/{namefile}.json') as file:
#             response = json.loads(file.read())
#             out_d[f"{namefile}"] = response
#     return out_d


def test():
    # get_from_json_file()
    # get_json_from_esi_to_file()
    # add_systems_id_in_DB()
    # get_constellations_to_json_file()
    # get_regions_to_json_file()
    # data = get_from_json_file()
    # add_systems_id_in_DB(data["systems"])
    # add_constellations_id_in_DB(data["constellations"])
    # add_regions_id_in_DB(data["regions"])
    ...




if __name__ == "__main__":
    test()

