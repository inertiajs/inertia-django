from django import forms

class TestForm(forms.Form):
    str_field = forms.CharField(max_length=100, required=True)
    num_field = forms.IntegerField(min_value=20, required=True)
