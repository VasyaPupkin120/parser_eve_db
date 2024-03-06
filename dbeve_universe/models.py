from django.db import models
from django.db.models.deletion import CASCADE
# вообще все списки в моделях с внешими ссылками -
# должны быть просто менедеждеры обратной связи

# в конце всех моделей есть Types и Groups - набор объектов - их список можно получить отдельным запросом.
# Types и Groups надо отдельно загрузить

# схема зависимостей моделей - 
# Regions
# Constellations
# Systems
#    Star
#         Types
#             Groups
#    Celestials
#        Planets
#        Moons
#        Asteroid_belts

# отдельные модели типов и групп - их прям дохрена и не понятно зачем их всех
# надо парсить по мере необходимости - только когда они попадаются в запросе.
# при парсинге нужно создавать группу, если этой группы еще нет и связанный с ней тип
# Groups
#     Types


# Create your models here.
class Regions(models.Model):
    # вместо поля constellations - менеджер обратной связи на модель Constellations
    description = models.TextField(null=True)
    name = models.CharField(null=True)
    region_id = models.IntegerField(primary_key=True)

class Constellations(models.Model):
    constellation_id = models.IntegerField(primary_key=True)
    name = models.CharField(null=True)
    position_x = models.IntegerField(null=True)
    position_y = models.IntegerField(null=True)
    position_z = models.IntegerField(null=True)
    region_id = models.ForeignKey("Regions",on_delete=models.CASCADE, primary_key=True)
    # вместо поля systems - менеджер обратной связи на модель Systems

class Systems(models.Model):
    constellation_id = models.ForeignKey("Constellations", on_delete=CASCADE, primary_key=True)
    name = models.CharField(null=True)
    # вместо поля plantes - менеджер обратной связи на модель Celestials
    position_x = models.IntegerField(null=True)
    position_y = models.IntegerField(null=True)
    position_z = models.IntegerField(null=True)
    security_class = models.CharField(null=True)
    security_status = models.FloatField(null=True)
    # вместо поля star_id - менеджер обратной связи на модель Star
    # здесь закончил писать про связи
    stargates = models.JSONField(null=True)
    stations = models.JSONField(null=True)
    system_id = models.IntegerField(primary_key=True)

class Star(models.Model):
    """
    Вторична для Systems
    Модель одной звезды
    """
    age = models.IntegerField(null=True)
    luminosity = models.FloatField(null=True)
    name = models.CharField(null=True)
    radius = models.IntegerField(null=True)
    solar_system_id = models.OneToOneField("Systems", on_delete=CASCADE, null=True)
    spectral_class = models.CharField(null=True)
    temperature = models.IntegerField(null=True)
    type_id = models.IntegerField(null=True)

class Celestials(models.Model):
    """
    Вторична для Systems
    Объединяет группу из планеты, лун, белтов
    """
    ...
class Plantes(models.Model):
    """
    Вторична для Celestials.
    """
class Moons(models.Model):
    """
    Вторична для Celestials
    """
    moon_id = models.IntegerField(null=True)
    name = models.CharField(null=True)
    position_x = models.IntegerField(null=True)
    position_y = models.IntegerField(null=True)
    position_z = models.IntegerField(null=True)
    system_id = models.ForeignKey("Celestials", on_delete=models.CASCADE, null=True)
class Asteroid_belts(models.Model):
    """
    Вторична для Celestials
    """
    ...


class Groups(models.Model):
    """
    Группы типов
    """
    ...

class Types(models.Model):
    """
    вторичная для Groups
    содержит судя по всему все итемы
    """
    group_id = models.ForeignKey("Groups", on_delete=CASCADE, null=True)
    ...
