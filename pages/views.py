from django.shortcuts import render

# Create your views here.

def index(requests):
    return render(requests, "pages/index.html")

def db_overview(requests):
    return render(requests, "pages/dbeve_overview.html")

