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
        #context['form'] = forms.AddItemToRecipeForm
            
        return context

def add_recipe(request):

	IngredientFormSet = formset_factory(IngredientForm, max_num=20, min_num=1, validate_min=True, extra=0)

	if request.method == "POST":		
		form = forms.AddRecipeForm(request.POST)
		ingredient_formset = IngredientFormSet(request.POST)
	    
		if form.is_valid() and ingredient_formset.is_valid():
			# Get basic recipe information
			name = form.cleaned_data['name']
			prepTime = form.cleaned_data['prepTime']
			servings = form.cleaned_data['servings']
			category = form.cleaned_data['category']
			instructions = form.cleaned_data['instructions']
			externalLink = form.cleaned_data['externalLink']

			if Recipe.objects.filter(name=name).exists():
				messages.warning(request, "Recipe already exists")
				return HttpResponseRedirect(reverse('recipes:new_recipe'))

			# redirect to new recipe after creation
			else:
				# add other fields
				new_recipe = Recipe.objects.create(
					name=name, 
					date=timezone.now(),
					prepTime=prepTime,
					servings=servings,
					category=category,
					instructions=instructions,
					externalLink=externalLink)

				# Save ingredients for each form in the formset
				new_ingredients = []

				for ingredient_form in ingredient_formset:
					ingredient = ingredient_form.cleaned_data['value']
					food_item = ingredient_form.cleaned_data['foodItem']

					if ingredient:
						new_ingredient_link = RecipeIngredients.objects.create(
							recipe=new_recipe, 
							ingredient=ingredient,
							foodItem=food_item)

						new_ingredients.append(new_ingredient_link)
				
				try:
					with transaction.atomic():
						RecipeIngredients.objects.bulk_create(new_ingredients)
						messages.success(request, "You have successfully added a recipe")

						return HttpResponseRedirect(reverse('recipes:detail', args = (new_recipe.id,)))
				except IntegrityError:
					messages.warning(request, "There was an error saving your recipe")
					return HttpResponseRedirect(reverse('recipes:new_recipe'))
   

	# if method = GET, then return a blank form
	else:
		form = forms.AddRecipeForm()
		ingredient_formset = IngredientFormSet()

	context = {
	    'form': form,
	    'ingredient_formset': ingredient_formset
	}

	return render(request, 'recipes/new_recipe.html', context)

