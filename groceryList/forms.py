from django import forms
from django.forms import Form, ModelForm, TextInput
from .models import FoodItem, GroceryList

class AddListForm(Form):
    name = forms.CharField(label = 'Add new grocery list', max_length = 100,
                           empty_value = "None")

class AddGroceryListForm(forms.ModelForm):
    
    class Meta:
        model = GroceryList
        fields = ['name']
    
class AddItemToListForm(Form):
    food_item = forms.CharField(label = 'Add an item to your grocery list',
                                max_length = 100, required = True)
    quantity = forms.IntegerField(max_value=100, min_value=0)
