from django import forms

class ParseOneSystemForm(forms.Form):
    system_id = forms.IntegerField()
    # request = forms.CharField(label="запрос")
