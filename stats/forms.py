'''from django import forms
from django.forms import ModelChoiceField'''


class FilterForm(forms.form):
    choices = ['Name', 'Most Consumed', 'Least Consumed']
    select = forms.ModelChoiceField(queryset=choices,
     required=False, label='Filter')
