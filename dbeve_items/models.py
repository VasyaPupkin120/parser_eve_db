from django.db import models
from config.models import BaseEntity

class Categories(BaseEntity):
    """
    Категории итемов.
    """
    category_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(null=True)
    published = models.BooleanField(null=True)


class Groups(BaseEntity):
    """
    Группы итемов.
    """
    group_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(null=True)
    published = models.BooleanField(null=True)

    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True)


class Types(BaseEntity):
    """
    Типы итемов.
    """
    capacity = models.BigIntegerField(null=True)
    description = models.TextField(null=True)
    mass = models.DecimalField(max_digits=40, decimal_places=0, null=True) # некоторые планеты очень тяжелые, поэтому такое большое число
    name = models.CharField(null=True)
    packaged_volume = models.BigIntegerField(null=True)
    portion_size = models.BigIntegerField(null=True)
    published = models.BooleanField(null=True)
    radius = models.BigIntegerField(null=True)
    type_id = models.BigIntegerField(primary_key=True)
    volume = models.BigIntegerField(null=True)

    group = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True)
    # graphic = models.ForeignKey("хз куда то там на модель графики", null=True)
    # icon = models.ForeignKey("куда то на модель изображения, типа есть рендер - чуть качественее и есть icon - не настолько качественнео изображение", null=True)
