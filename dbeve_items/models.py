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
    type_id = models.BigIntegerField(primary_key=True)
