from django.shortcuts import render
from .models import Alliances, Characters, Corporations

# Create your views here.

def social(request):
    return render(request, "dbeve_social/social.html")


def one_alliance(request, alliance_id):
    alliance = Alliances.objects.get(alliance_id=alliance_id)
    return render(request, "dbeve_social/one_alliance.html", context={"alliance": alliance,})


def all_alliances(request):
    alliances = Alliances.objects.all()[:100]
    return render(request, "dbeve_social/all_alliances.html", context={"alliances": alliances,})


def all_corporations(request):
    corporations = Corporations.objects.all()[:100]
    return render(request, "dbeve_social/all_corporations.html", context={"corporations": corporations,})

def all_characters(request):
    characters = Characters.objects.all()[:100]
    return render(request, "dbeve_social/all_characters.html", context={"characters": characters,})
