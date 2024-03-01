from django.shortcuts import render
from .models import ResultJSON
from requests_to_esi.forms import RequestSystemForm
from .services import request_data_one_system

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
