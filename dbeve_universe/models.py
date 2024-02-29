from django.db import models

# Create your models here.
class Systems(models.Model):
    constellation_id = models.IntegerField(null=True)
    name = models.CharField(null=True)
    planets = models.JSONField(null=True)
    position = models.JSONField(null=True)
    security_class = models.CharField(null=True)
    security_status = models.FloatField(null=True)
    star_id = models.IntegerField(null=True)
    stargates = models.JSONField(null=True)
    stations = models.JSONField(null=True)
    system_id = models.IntegerField(primary_key=True)

class Regions(models.Model):
    name = models.CharField(null=True)
    region_id = models.IntegerField(primary_key=True)

class Constellations(models.Model):
    name = models.CharField(null=True)
    constellation_id = models.IntegerField(primary_key=True)
