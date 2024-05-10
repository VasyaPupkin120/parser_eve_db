from django.db.models import F, Q, BooleanField, Case, When
from django.db.models.functions import Ceil
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from dbeve_social.models import Battlereports, Characters, Killmails

# Create your views here.

def brs_and_parsing(request):
    """
    Страничка с формой ввода для парсинга бр-а и с выводом списка уже 
    спарсенных бр-ов. 
    """
    battlereports = Battlereports.objects.all()[:100]
    return render(request, "compensation/brs_and_parsing.html", context={"battlereports": battlereports,})
    

def markup_battlereport(request, battlereport_id):
    """
    Собственно страничка для формирования списка компенсаций.
    """
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

    return render(request, "compensation/markup_battlereport.html",
                  context={
                      "killmails": killmails,
                      "battlereport": battlereport,
                      # "checked_killmails": checked_killmails,
                      })



def notes_compensations(request:HttpRequest):
    if request.method == "POST":
        data = dict(request.POST)
        compensations = []
        for key, value in data.items():
            if len(value) == 2 and value[0] == "on":
                killmail = Killmails.objects.get(killmail_id=key)
                char = killmail.victim.character
                one_compensation = f"<url=showinfo:1375//{key}>{char.name}</url> {value[1]}"
                compensations.append(one_compensation)
        print(compensations)
        return render(request, "compensation/notes_compensations.html", {"compensations": compensations})
        
