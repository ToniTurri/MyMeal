from django import forms

class AddListForm(forms.Form):
    name = forms.CharField()

class AddRecipeForm(forms.Form):
    name = forms.CharField()
    
class AddItemToListForm(forms.Form):
    food_item = forms.CharField(label = 'Add item to grocery list', max_length=100)
    
class AddItemToRecipeForm(forms.Form):
    food_item = forms.CharField()