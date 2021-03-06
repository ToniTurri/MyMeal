from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.utils import timezone
from django.contrib import messages
from django.views.generic.edit import CreateView
from .models import Recipe, RecipeIngredients
from inventory.models import InventoryItem
from inventory.views import generic_foods
from recipeFinder.views import find_InventoryItem
from recipeFinder.views import find_generic_item
from groceryList.models import GroceryList, GroceryItems
from .forms import IngredientForm
from . import forms
from django.forms.formsets import formset_factory
from django.db import IntegrityError, transaction


class IndexView(ListView):
    model = Recipe
    template_name = 'recipes/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['all_recipes'] = Recipe.objects.filter(user=self.request.user)

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
        recipe = self.get_object()
        if recipe.user != self.request.user:
            raise Http404()

        context['ingredients'] = RecipeIngredients.objects.filter(recipe=self.kwargs.get('pk'))

        return context


def delete_recipe(request, pk):
    if request.method == 'POST':
        Recipe.objects.filter(user=request.user, id=pk).delete()
        return HttpResponseRedirect(reverse('recipes:index'))


def add_recipe(request, pk=0):
    is_edit = False
    IngredientFormSet = formset_factory(IngredientForm, max_num=20, min_num=1, validate_min=True, extra=0)

    if pk:
        is_edit = True
        try:
            recipe = Recipe.objects.filter(user=request.user, pk=pk).first()
            if recipe is None:
                raise Http404
            ingredients = RecipeIngredients.objects.filter(recipe=recipe.id)
            ingredient_data = [{'value': i.ingredient, 'inventoryItem': i.inventoryItem}
                               for i in ingredients]

            ingredient_formset = IngredientFormSet(initial=ingredient_data)
        except Recipe.DoesNotExist:
            recipe = Recipe()
            ingredient_formset = IngredientFormSet()
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
            nameExists = Recipe.objects.filter(user=request.user, name=name).exists()
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
                        user=request.user,
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
                    if ingredient_form.is_valid():
                        ingredient_line = ingredient_form.cleaned_data['value']
                        # try and link the ingredient to an inventory item
                        inventory_item = find_InventoryItem(ingredient_line, request.user)
                        # inventory_item = ingredient_form.cleaned_data['inventoryItem']

                        if ingredient_line:
                            new_ingredient_link = RecipeIngredients(
                                recipe=linked_recipe,
                                ingredient=ingredient_line,
                                inventoryItem=inventory_item)

                            new_ingredients.append(new_ingredient_link)

                try:
                    with transaction.atomic():
                        if is_edit:
                            # drop and recreate ingredients for ease
                            ingredients.delete()

                        RecipeIngredients.objects.bulk_create(new_ingredients)

                        return HttpResponseRedirect(reverse('recipes:detail', args=(linked_recipe.id,)))
                except IntegrityError:
                    messages.warning(request, "There was an error saving your recipe")
                    return HttpResponseRedirect(reverse('recipes:new_recipe'))

    context = {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'is_edit': is_edit,
        'id': recipe.id,
        'food_suggestions': generic_foods + \
                            [x for x in list(InventoryItem.objects.filter(user=request.user).values_list('name',
                                                                                                         flat=True).distinct())
                             if x not in generic_foods]
    }

    return render(request, 'recipes/new_recipe.html', context)


def create_grocery_list(request, pk):
    recipe = Recipe.objects.filter(user=request.user, id=pk).first()
    if recipe is None:
        raise Http404

    new_name = "For Recipe: " + str(recipe.name)

    if GroceryList.objects.filter(user=request.user, name=new_name).exists():
        messages.warning(request, "Grocery List Already Exists!")
        list_id = GroceryList.objects.filter(user=request.user, name=new_name).first().id
        return HttpResponseRedirect(reverse('groceryList:detail', args=(list_id,)))

    ingredients = RecipeIngredients.objects.filter(recipe=recipe)
    new_list = GroceryList.objects.create(user=request.user, name=new_name, date=timezone.now())

    for i in ingredients:
        inventoryItem = find_InventoryItem(i.ingredient, request.user)
        new_food = GroceryItems(groceryList=new_list,
                                name=inventoryItem.name if inventoryItem else find_generic_item(i.ingredient),
                                date=timezone.now(),
                                inventoryItem=inventoryItem)

        # no name found? don't add ingredient
        if not new_food.name:
            continue

        # avoid duplicates
        if GroceryItems.objects.filter(groceryList=new_list, name=new_food.name):
            continue

        new_food.save()


    return HttpResponseRedirect(reverse('groceryList:detail', args=(new_list.id,)))
