from django import forms
from django.forms import Form, ModelForm, TextInput
from .models import FoodItem, GroceryList, Recipe

class AddListForm(Form):
    name = forms.CharField(label = 'Add new grocery list', max_length = 100,
                           empty_value = "None")

class AddGroceryListForm(forms.ModelForm):
    
    class Meta:
        model = GroceryList
        fields = ['name']

class AddRecipeForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        fields = ['name']
    
class AddItemToListForm(Form):
    food_item = forms.CharField(label = 'Add an item to your grocery list',
                                max_length = 100, required = True)

class AddItemToRecipeForm(Form):
    food_item = forms.CharField(label = 'Add ingredient to recipe',
                           max_length = 100, required = True)

class AddRecipeToListForm(Form):
    recipe_name = forms.CharField(label = 'Add a recipe to your grocery list',
                           max_length = 100, required = True)