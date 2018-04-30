from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.utils import timezone
from django.contrib import messages
from django.db.models import F
from django.views.generic.edit import CreateView
from .models import Recipe, RecipeIngredients
from .forms import IngredientForm
from groceryList.models import FoodItem
from . import forms
from django.forms.formsets import formset_factory
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
   
#from django.contrib.auth.decorators import login_required
#@login_required(login_url='/accounts/login/')
class IndexView(ListView):
    model = Recipe
    template_name = 'recipes/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['all_recipes'] = Recipe.objects.all()
        
        return context

class NewRecipeView(CreateView):
    model = Recipe
    form_class = forms.AddRecipeForm
    form_class_new = forms.AddRecipeForm

    template_name = 'recipes/new_recipe.html'

class RecipeView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe.html'   
   
    def get_context_data(self, **kwargs):
        context = super(RecipeView, self).get_context_data(**kwargs)
        context['ingredients'] = RecipeIngredients.objects.filter(recipe=self.kwargs.get('pk'))
            
        return context

def delete_recipe(request, pk):
	if request.method == 'POST':
		Recipe.objects.filter(id=pk).delete()
		return HttpResponseRedirect(reverse('recipes:index'))

def add_recipe(request, pk=0):

	is_edit = False
	IngredientFormSet = formset_factory(IngredientForm, max_num=20, min_num=1, validate_min=True, extra=0)

	if pk:
		is_edit = True
		recipe = Recipe.objects.get(pk=pk)
		ingredients = RecipeIngredients.objects.filter(recipe=pk)
		ingredient_data = [{'value': i.ingredient, 'inventoryItem': i.inventoryItem}
							for i in ingredients]

		ingredient_formset = IngredientFormSet(initial=ingredient_data)
	else:
		recipe = Recipe()
		ingredient_formset = IngredientFormSet()

	form = forms.AddRecipeForm(instance=recipe, data=request.POST or None)

	if request.method == "POST":
		ingredient_formset = IngredientFormSet(request.POST)

		if form.is_valid() and ingredient_formset.is_valid():
			# Get basic recipe information
			name = form.cleaned_data['name']
			prepTime = form.cleaned_data['prepTime']
			servings = form.cleaned_data['servings']
			category = form.cleaned_data['category']
			instructions = form.cleaned_data['instructions']
			externalLink = form.cleaned_data['externalLink']

			# Error if the name of a recipe is taken when the recipe is new
			# or the user is editing an existing recipe
			nameExists = Recipe.objects.filter(name=name).exists()
			if (not is_edit or (is_edit and recipe.name != name)) and nameExists:
				messages.warning(request, "Recipe already exists")

			# redirect to new recipe after creation
			else:

				image = None
				if 'image' in request.FILES:
					image = request.FILES['image']

				if not is_edit:
					# add other fields
					new_recipe = Recipe.objects.create(
						name=name, 
						date=timezone.now(),
						prepTime=prepTime,
						servings=servings,
						category=category,
						instructions=instructions,
						externalLink=externalLink,
						image=image)

				else:
					# update fields
					recipe.name = name
					recipe.prepTime = prepTime
					recipe.servings = servings
					recipe.category = category
					recipe.instructions = instructions
					recipe.externalLink = externalLink
					recipe.image = image
					recipe.save()

				# Save ingredients for each form in the formset
				new_ingredients = []

				if is_edit:
					linked_recipe = recipe
				else:
					linked_recipe = new_recipe

				for ingredient_form in ingredient_formset:
					ingredient = ingredient_form.cleaned_data['value']
					inventory_item = ingredient_form.cleaned_data['inventoryItem']

					if ingredient:
						new_ingredient_link = RecipeIngredients(
							recipe=linked_recipe, 
							ingredient=ingredient,
							inventoryItem=inventory_item)

						new_ingredients.append(new_ingredient_link)
				
				try:
					with transaction.atomic():
						if is_edit:
							# drop and recreate ingredients for ease
							ingredients.delete()

						RecipeIngredients.objects.bulk_create(new_ingredients)

						return HttpResponseRedirect(reverse('recipes:detail', args = (linked_recipe.id,)))
				except IntegrityError:
					messages.warning(request, "There was an error saving your recipe")
					return HttpResponseRedirect(reverse('recipes:new_recipe'))

	context = {
	    'form': form,
	    'ingredient_formset': ingredient_formset,
	    'is_edit': is_edit,
	    'id': recipe.id
	}

	return render(request, 'recipes/new_recipe.html', context)

