from django import forms
from django.forms import Form, ModelForm, TextInput, ModelChoiceField
from .models import GroceryItems, GroceryList
from inventory.models import InventoryItem

class AddListForm(Form):
    name = forms.CharField(label = 'Add new grocery list', max_length = 100, empty_value = "None")

class AddGroceryListForm(forms.ModelForm):
    
    class Meta:
        model = GroceryList
        fields = ['name']
    
class AddItemToListForm(Form):
    name = forms.CharField(label = 'Item', max_length = 100, required=False)
    quantity = forms.IntegerField(max_value=100, min_value=1, required=False, initial = 1)
    inventory_item = forms.ModelChoiceField(queryset=InventoryItem.objects.all(), required=False)
