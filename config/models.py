from django.db import models

class BaseEntity(models.Model):
    dt_change = models.DateTimeField(auto_now=True, null=True)
    response_body = models.JSONField(null=True)
    class Meta:
        abstract = True
