from django.db import models
from config.models import BaseEntity
from dbeve_universe.models import Systems, Stations, Bloodlines, Races, Factions
from dbeve_items.models import Items, ShipTypes, WeaponTypes


class Alliances(BaseEntity):
    """
    Изображение хранится в static/img/alliances, без связи через БД. Находить изображение
    по id и разрешению.

    """
    alliance_id = models.BigIntegerField(primary_key=True)
    date_founded = models.DateTimeField(null=True) # поле приходит вида "2010-11-04T13:11:00Z"
    name = models.CharField(null=True)
    ticker = models.CharField(null=True)
    nameicon = models.CharField(null=True)
    
    creator = models.ForeignKey("Characters", on_delete=models.SET_NULL, null=True, related_name="creator_alliance")
    creator_corporation = models.ForeignKey("Corporations", on_delete=models.SET_NULL, null=True, related_name="creator_corporation")
    executor_corporation = models.OneToOneField("Corporations", on_delete=models.SET_NULL, null=True, related_name="executor_corporation")


class Corporations(BaseEntity):
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


class Characters(BaseEntity):
    character_id = models.BigIntegerField(primary_key=True)
    birthday = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    gender = models.CharField(null=True)
    is_deleted = models.BooleanField(null=True)
    name = models.CharField(null=True)
    nameicon = models.CharField(null=True)
    security_status = models.FloatField(null=True)
    title = models.TextField(null=True)

    alliance = models.ForeignKey("Alliances", on_delete=models.SET_NULL, null=True)
    bloodline = models.ForeignKey(Bloodlines, on_delete=models.SET_NULL, null=True)
    corporation = models.ForeignKey("Corporations", on_delete=models.SET_NULL, null=True)
    faction = models.ForeignKey(Factions, on_delete=models.SET_NULL, null=True)
    race = models.ForeignKey(Races, on_delete=models.SET_NULL, null=True)


class VictimItems(models.Model):
    """
    Вспомогательная модель для пострадавшего - итемы в 
    Для описания итемов, выпавших с пострадавшего.
    Нет нужды в поле response_body и dt_change.
    """
    flag = models.BigIntegerField()
    # итем может быть унижчтожен или дропнут. И то и то должно быть в каком то количестве
    status = models.CharField(choices=(("destroyed", "Итем уничтожен"), ("dropped", "Итем выпал")))
    quantity = models.BigIntegerField()

    item_type = models.ForeignKey(Items, on_delete=models.SET_NULL, null=True)
    victim = models.ForeignKey("Victim", on_delete=models.CASCADE, related_name="items")

class Victim(models.Model):
    """
    Вспомогательная модель для киллмыла - пострадавший. 
    Нет нужды в поле response_body и dt_change.
    """
    damage_taken = models.BigIntegerField()

    alliance = models.OneToOneField("Alliances", on_delete=models.SET_NULL, null=True)
    character = models.OneToOneField("Characters", on_delete=models.CASCADE, null=True)
    corporation = models.OneToOneField("Corporations", on_delete=models.SET_NULL, null=True)
    killmail = models.OneToOneField("Killmails", on_delete=models.CASCADE, related_name="victim")

class Attackers(models.Model):
    """
    Вспомогательная модель для киллмыла - запись об одном атакующем.
    """
    damage_done = models.BigIntegerField()
    final_blow = models.BooleanField()
    security_status = models.FloatField()

    alliance = models.OneToOneField("Alliances", on_delete=models.SET_NULL, null=True)
    character = models.OneToOneField("Characters", on_delete=models.CASCADE, null=True)
    corporation = models.OneToOneField("Corporations", on_delete=models.SET_NULL, null=True)
    killmail = models.ForeignKey("Killmails", on_delete=models.CASCADE, related_name="attackers")
    ship_type = models.ForeignKey(ShipTypes, on_delete=models.SET_NULL, null=True)
    weapon_type = models.ForeignKey(WeaponTypes, on_delete=models.SET_NULL, null=True)

class Killmails(BaseEntity):
    """
    Класс одиночного киллмыла
    """
    killmail_id = models.BigIntegerField(primary_key=True)
    killmail_time = models.DateTimeField()
    position_x = models.DecimalField(max_digits=32, decimal_places=0)
    position_y = models.DecimalField(max_digits=32, decimal_places=0)
    position_z = models.DecimalField(max_digits=32, decimal_places=0)

    solar_system = models.ForeignKey(Systems, on_delete=models.SET_NULL, null=True)
    ship_type = models.ForeignKey(ShipTypes, on_delete=models.SET_NULL, null=True)
