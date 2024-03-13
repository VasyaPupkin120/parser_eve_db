from django.db import models

class Alliances(models.Model):
    """
    Изображение хранится в static/img/alliances, без связи через БД. Находить изображение
    по id и разрешению.
    """
    # creator_corporation - поле внешнего ключа со связью один-к-одному на корпорацию 
    # creator - один-к-одному на конкретного персонажа
    # executor_corporation - один-к-одному на корпорацию
    alliance_id = models.BigIntegerField(primary_key=True)
    date_founded = models.DateTimeField(null=True) # поле приходит вида "2010-11-04T13:11:00Z"
    name = models.CharField(null=True)
    ticker = models.CharField(null=True)
    response_body = models.JSONField(null=True)
    nameicon = models.CharField(null=True)




