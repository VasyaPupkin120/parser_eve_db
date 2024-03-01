import requests
from .models import ResultJSON

def request_data_one_system(system_id):
    url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/?datasource=tranquility&language=en"
    response = requests.get(url).json()
    ResultJSON.objects.create(request=url, response=response)
