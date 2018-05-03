from django import forms
from django.forms import Form

class AddItemToInventoryForm(Form):
    name = forms.CharField(label='Item', max_length=100, required=True)