from django import forms
from groceryList.models import GroceryList

class BarcodeForm(forms.Form):
    number = forms.CharField(label='Barcode Number', max_length=13)

class listSelectionForm(forms.ModelForm):
    class Meta:
        model = GroceryList
        fields = ['name']