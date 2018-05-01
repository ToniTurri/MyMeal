from django import forms

# class RecipeSearchForm(forms.Form):
    # not yet implemented

class IngredientInputForm(forms.Form):
    item = forms.CharField(max_length=100, widget=forms.TextInput(), required=True)

    def __init__(self, *arg, **kwarg):
		      super(IngredientInputForm, self).__init__(*arg, **kwarg)
