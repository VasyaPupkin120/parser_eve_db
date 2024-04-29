from django.shortcuts import render
from .models import Alliances, Characters, Corporations, Relates

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

def all_relates(request):
    relates = Relates.objects.all()[:100]
    return render(request, "dbeve_social/all_relates.html", context={"relates": relates,})

def one_related(request, related_id):
    related = Relates.objects.get(related_id=related_id)
    killmails = related.killmails.all()
    return render(request, "dbeve_social/one_related.html", context={"related": related , "killmails": killmails})
