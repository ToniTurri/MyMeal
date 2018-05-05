from django import forms
from django.forms import Form, formsets, ModelChoiceField
from .models import Recipe
from inventory.models import InventoryItem
from django.forms.formsets import formset_factory, BaseFormSet


class IngredientForm(forms.Form):
    value = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'autocomplete'}),
                            required=True)
    inventoryItem = forms.ModelChoiceField(queryset=InventoryItem.objects.all(), required=False)

    def __init__(self, *arg, **kwarg):
        super(IngredientForm, self).__init__(*arg, **kwarg)


class AddRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'prepTime', 'servings', 'category', 'instructions', 'externalLink', 'image']
        widgets = {
            'category': forms.Select(),
            'instructions': forms.Textarea(),
            'externalLink': forms.URLInput(),
            'image': forms.ClearableFileInput()
        }
