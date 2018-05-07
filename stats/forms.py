from django import forms
from django.forms import ChoiceField


class FilterForm(forms.Form):
    CHOICES = (('1', 'Name',), ('2', 'Most Consumed',), ('3', 'Least Consumed',))
    choice_field = forms.ChoiceField(choices=CHOICES)
