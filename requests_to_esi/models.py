from django.db import models

# Create your models here.

#FIXME
# нужно эту модель преобразовать в модель-лог, чтобы каждый запрос к esi
# логировался независимо от результата
class ResultJSON(models.Model):
    # status - поле для записи информации об запросе, типа успешен, или нет, или что то не так пошло и что именно
    # status_code - собственно код ответа
    # type_exception - тип вознкшего исключения
# limit_remain = 
# limit_reset = 
# error_limited = 
# error_message = поля для хранения существенных заголовков ответа
    request = models.TextField()
    response = models.JSONField()
    date = models.DateTimeField(auto_now=True)


