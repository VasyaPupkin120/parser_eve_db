from django.db import models
from dbeve_universe.models import Stations, Bloodlines, Races, Factions


class Alliances(models.Model):
    """
    Изображение хранится в static/img/alliances, без связи через БД. Находить изображение
    по id и разрешению.

    """
    alliance_id = models.BigIntegerField(primary_key=True)
    date_founded = models.DateTimeField(null=True) # поле приходит вида "2010-11-04T13:11:00Z"
    name = models.CharField(null=True)
    ticker = models.CharField(null=True)
    nameicon = models.CharField(null=True)
    
    creator = models.OneToOneField("Characters", on_delete=models.SET_NULL, null=True, related_name="creator_alliance")
    creator_corporation = models.OneToOneField("Corporations", on_delete=models.SET_NULL, null=True, related_name="creator_corporation")
    executor_corporation = models.OneToOneField("Corporations", on_delete=models.SET_NULL, null=True, related_name="executor_corporation")

    response_body = models.JSONField(null=True)


class Corporations(models.Model):
    """
    """
    corporation_id = models.BigIntegerField(primary_key=True)
    date_founded = models.DateTimeField(null=True) # поле приходит вида "2010-11-04T13:11:00Z"
    description = models.TextField(null=True)
    member_count = models.BigIntegerField(null=True)
    name = models.CharField(null=True)
    nameicon = models.CharField(null=True)
    shares = models.BigIntegerField(null=True)
    ticker = models.CharField(null=True)
    tax_rate = models.FloatField(null=True)
    url = models.CharField(null=True)
    war_eligible = models.BooleanField(null=True)

    alliance = models.ForeignKey("Alliances", on_delete=models.SET_NULL, null=True)
    ceo = models.ForeignKey("Characters", on_delete=models.SET_NULL, null=True, related_name="ceo")
    creator = models.ForeignKey("Characters", on_delete=models.SET_NULL, null=True, related_name="creator_corporation")
    faction = models.ForeignKey(Factions, on_delete=models.SET_NULL, null=True)
    home_station = models.ForeignKey(Stations, on_delete=models.SET_NULL, null=True)

    response_body = models.JSONField(null=True)


class Characters(models.Model):
    character_id = models.BigIntegerField(primary_key=True)
    birthday = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    gender = models.CharField(null=True)
    name = models.CharField(null=True)
    nameicon = models.CharField(null=True)
    security_status = models.FloatField(null=True)
    title = models.TextField(null=True)

    alliance = models.ForeignKey("Alliances", on_delete=models.SET_NULL, null=True)
    bloodline = models.ForeignKey(Bloodlines, on_delete=models.SET_NULL, null=True)
    corporation = models.ForeignKey("Corporations", on_delete=models.SET_NULL, null=True)
    faction = models.ForeignKey(Factions, on_delete=models.SET_NULL, null=True)
    race = models.ForeignKey(Races, on_delete=models.SET_NULL, null=True)

    response_body = models.JSONField(null=True)


