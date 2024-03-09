from django import forms

class RequestSystemForm(forms.Form):
    system_id = forms.IntegerField()
    # request = forms.CharField(label="запрос")
