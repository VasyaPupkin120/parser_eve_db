from django.db import models

# Create your models here.
class ResultJSON(models.Model):
    request = models.TextField()
    response = models.JSONField()
    date = models.DateTimeField(auto_now=True)
