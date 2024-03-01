from django import forms
from .models import ResultJSON

class RequestSystemForm(forms.Form):
    system_id = forms.IntegerField()
    # request = forms.CharField(label="запрос")
