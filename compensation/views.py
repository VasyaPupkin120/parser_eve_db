import asyncio


from django.db.models import F, Q, BooleanField, Case, When
from django.db.models.functions import Ceil
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import resolve, reverse

from dbeve_social.models import Battlereports, Characters, Killmails
from requests_to_esi.services import parser_battlereport, base_requests

# Create your views here.

def brs_and_parsing(request):
    """
    Страничка с формой ввода для парсинга бр-а и с выводом списка уже 
    спарсенных бр-ов. 
    """
    battlereports = Battlereports.objects.all().order_by("-time_end")[:100]
    return render(request, "compensation/brs_and_parsing.html", context={"battlereports": battlereports,})
    

def markup_battlereport(request, battlereport_id):
    """
    Собственно страничка для формирования списка компенсаций.
    """
    battlereport = Battlereports.objects.get(battlereport_id=battlereport_id)

    killmails = battlereport.killmails.all()
    killmails_ids = [killmail.killmail_id for killmail in killmails]

    # блок для проверки, какие киллмыла нужно заранее помечать как готовые к компенсациям.
    friend_alliances = [99012122, 99012328, 99011248, 99012287]
    friend_corporations = [98733526]
    this_friend_alliance = Q(victim__alliance_id__in=friend_alliances)
    this_friend_corporation = Q(victim__corporation_id__in=friend_corporations)
    this_more_than = Q(sumv__gt=100000)
    checked_killmails = killmails.filter((this_friend_alliance | this_friend_corporation) & this_more_than)
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

    killmails = killmails.order_by("-checked_for_compense","victim__alliance_id", "victim__corporation_id", "victim__character_id", "-round_sumv", )

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
        names_for_email = []
        for key, value in data.items():
            if len(value) == 2 and value[0] == "on":
                killmail = Killmails.objects.get(killmail_id=key)
                char = killmail.victim.character
                one_compensation = f"<url=showinfo:1375//{char.character_id}>{char.name}</url> {value[1]} {killmail.victim.ship.name}"
                compensations.append(one_compensation)
                if char.name not in names_for_email:
                     names_for_email.append(char.name)
        names_for_email =  ", ".join(names_for_email)
        battlereport = data["battlereport"][0] # не понимаю почему поле формы hidden отправляет список, но окей
        body_mail = f'<font size="14" color="#bfffffff"></font><font size="13" color="#bfffffff">Привет! <br><br>Отправил компенс за бой </font><font size="13" color="#ffffe400"><loc><a href="http://br.evetools.org/br/{battlereport}">https://br.evetools.org/br/{battlereport}</a></loc><br><br></font><font size="13" color="#bfffffff">Проверьте, на всякий случай :)<br><br>Вы лучшие!</font>'

        return render(request, "compensation/notes_compensations.html", {"compensations": compensations, "battlereport": battlereport, "names_for_email": names_for_email, "body_mail": body_mail})
        


def parse_battlereport(request):
    """
    На post-запрос парсит бр с помощью уже имеющегося парсера бр-ов 
    и выполняет перенаправление на страничку разметки только что спарсенного бр-а.

    На get-запрос выполняет перенаправление на общую страничку компенсаций - 
    нефиг сюда вообще заходить по get-запросу.
    """
    if request.method == "POST":
        battlereport_id = request.POST.get("battlereport_id")
        if not battlereport_id:
            return
        try:
            asyncio.run(parser_battlereport.create_battlereport(battlereport_id))
        except base_requests.StatusCodeNot200Exception as e:
            #FIXME
            #FIXME
            # вызов какой то там странички в случае ошибки, я устал уже надо потом исправить
            return render(request, "requests_to_esi/dbeve_social/parse_one_battlereport.html", {"exception": e})
        return redirect(reverse("compensation:markup_battlereport", kwargs={"battlereport_id": battlereport_id}))
    return redirect(reverse("compensation:brs_and_parsing"))
