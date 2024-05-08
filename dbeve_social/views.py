from django.db.models import F, Q, BigIntegerField, BooleanField, Case, CharField, DecimalField, EmailField, ExpressionWrapper, IntegerField, Value, When
from django.db.models.functions import Ceil
from django.shortcuts import render
from django.urls.resolvers import CheckURLMixin
from .models import Alliances, Characters, Corporations, Battlereports, Killmails

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

def all_battlereports(request):
    battlereports = Battlereports.objects.all()[:100]
    return render(request, "dbeve_social/all_battlereports.html", context={"battlereports": battlereports,})

def one_battlereport(request, battlereport_id):
    battlereport = Battlereports.objects.get(battlereport_id=battlereport_id)

    killmails = battlereport.killmails.all()
    killmails_ids = [killmail.killmail_id for killmail in killmails]

    # блок для проверки, какие киллмыла нужно заранее помечать как готовые к компенсациям.
    friend_alliances = [99012122, 99004905]
    this_friend_alliance = Q(victim__alliance_id__in=friend_alliances)
    this_more_than = Q(sumv__gt=100000)
    checked_killmails = killmails.filter(this_friend_alliance & this_more_than)
    checked_killmails_ids = [checked_killmail.killmail_id for checked_killmail in checked_killmails]

    # блок добавления вычислимых полей
    # для измерения в миллионах + округление в большую сторону
    killmails = killmails.annotate(round_sumv=Ceil(F('sumv') / 1000000))
    # С помощью условных выражений СУБД (Case+When) создаю вычислимое поле checked_for_compense, 
    # в котором устанавливается отметка, нужно ли выделять в чекбоксе данное киллмыло
    killmails = killmails.annotate(
            checked_for_compense=Case(
                When(Q(killmail_id__in=checked_killmails_ids), True), 
                default=False,
                output_field=BooleanField()
                )
            )
    killmails = killmails.order_by("-checked_for_compense","victim__alliance_id", "-round_sumv", )

    return render(request, "dbeve_social/compense_battlereport.html",
                  context={
                      "killmails": killmails,
                      "battlereport": battlereport,
                      # "checked_killmails": checked_killmails,
                      })
