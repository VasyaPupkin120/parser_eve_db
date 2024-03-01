from django.shortcuts import render

# Create your views here.
def main_request(request):
    return render(request, "requests_to_esi/main_request.html")
