from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.utils import timezone
from django.contrib import messages
from django.db.models import F
from django.views.generic.edit import CreateView
from .models import GroceryList, FoodItem, Recipe
from . import forms
   

#from django.contrib.auth.decorators import login_required
#@login_required(login_url='/accounts/login/')
class IndexView(ListView):
    model = GroceryList
    template_name = 'groceryList/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['all_grocery_lists'] = GroceryList.objects.all()
        context['all_recipes'] = Recipe.objects.all()
        
        return context

class NewGroceryListView(CreateView):
    model = GroceryList
    template_name = 'groceryList/new.html'
    form_class = forms.AddGroceryListForm

    def get_context_data(self, **kwargs):
        context = super(NewGroceryListView, self).get_context_data(**kwargs)
        context['food_name'] = self.kwargs.get("food_name")

        return context

class NewRecipeView(CreateView):
    model = Recipe
    form_class = forms.AddRecipeForm
    form_class_new = forms.AddRecipeForm

    template_name = 'groceryList/new_recipe.html'
  
class GroceryListView(DetailView):
    model = GroceryList
    template_name = 'groceryList/detail.html'   
   
    def get_context_data(self, **kwargs):
        context = super(GroceryListView, self).get_context_data(**kwargs)
        context['item_form'] = forms.AddItemToListForm
        context['recipe_form'] = forms.AddRecipeToListForm
            
        return context

class RecipeView(DetailView):
    model = Recipe
    template_name = 'groceryList/recipe.html'   
   
    def get_context_data(self, **kwargs):
        context = super(RecipeView, self).get_context_data(**kwargs)
        context['form'] = forms.AddItemToRecipeForm
            
        return context
    
def add(request):
    if request.method == "POST":
        form = forms.AddGroceryListForm(request.POST)

        if form.is_valid():
            text = form.cleaned_data['name']
            
            # this is probably meant for add_to_list()
            scanned_food_name = request.POST.get("food_name")

            if GroceryList.objects.filter(name=text).exists():
                messages.warning(request, "Grocery list already exists")
                
                return HttpResponseRedirect(reverse('groceryList:new'))
            
            # redirect to new grocery list after creation
            else:        
                new_list = GroceryList.objects.create(name=text, date=timezone.now())

                # if we are making a list from the barcodeScan app, add the food item too
                if scanned_food_name is not None:
                    new_food = FoodItem(name=scanned_food_name, date=timezone.now())
                    new_food.save()
                    new_list.fooditems.add(new_food)

                return HttpResponseRedirect(reverse('groceryList:detail', args = (new_list.id,)))

    # if method = GET, then return a blank form
    else:
        form = forms.AddGroceryListForm()
    return render(request, 'groceryList:index', {'form':form})

def add_recipe(request):
    if request.method == "POST":
        form = forms.AddRecipeForm(request.POST)
        
        if form.is_valid():
            text = form.cleaned_data['name']

            if Recipe.objects.filter(name=text).exists():
                messages.warning(request, "Recipe already exists")
                
                return HttpResponseRedirect(reverse('groceryList:new_recipe'))
            
            # redirect to new recipe after creation
            else:        
                new_recipe = Recipe.objects.create(name=text, date=timezone.now())
                
                return HttpResponseRedirect(reverse('groceryList:recipe', args = (new_recipe.id,)))
    
    # if method = GET, then return a blank form
    else:
        form = forms.AddRecipeForm()
    return render(request, 'groceryList:index', {'form':form})

def add_to_list(request, pk):
    grocery_list = get_object_or_404(GroceryList, pk = pk)
    
    if request.method == "POST":
        form = forms.AddItemToListForm(request.POST)
        
        if form.is_valid():
            food = form.cleaned_data['food_item']
            qty = form.cleaned_data['quantity']

            # probably a good idea to ask the user if they want to do this
            if grocery_list.fooditems.filter(name=food).exists():
                grocery_list.fooditems.filter(name=food).update(quantity = F('quantity') + qty)
            else:
                new_food = FoodItem(name=food, quantity = qty, date=timezone.now())
                new_food.save()
                grocery_list.fooditems.add(new_food)
            
        return HttpResponseRedirect(reverse('groceryList:detail', args = (pk,)))
            

    else:
        form = forms.AddItemToListForm()
    
    return render(request, 'groceryList/detail.html', {'form': form})

def increment_food_item(request):
    pk = None
    if request.method == 'GET':
        pk = request.GET['list_id']
        food_item = request.GET['food_item']
    
    if pk:
        grocery_list = get_object_or_404(GroceryList, pk = pk)
        qty = grocery_list.fooditems.get(name=food_item).quantity
        grocery_list.fooditems.filter(name=food_item).update(quantity = F('quantity') + 1)

        return HttpResponse(qty + 1)
    return HttpResponse(0)

def decrement_food_item(request):
    pk = None
    if request.method == 'GET':
        pk = request.GET['list_id']
        food_item = request.GET['food_item']
    
    if pk:
        grocery_list = get_object_or_404(GroceryList, pk = pk)
        qty = grocery_list.fooditems.get(name=food_item).quantity
        
        # this doesn't work; probably tricky to make it happen here
        if qty == 0:
            grocery_list.fooditems.remove(food_item)
            grocery_list.save()
        
        else:
            grocery_list.fooditems.filter(name=food_item).update(quantity = F('quantity') - 1)
            return HttpResponse(qty - 1)
        
    return HttpResponse(0)

def add_recipe_to_list(request, pk):
    grocery_list = get_object_or_404(GroceryList, pk = pk)
    
    if request.method == "POST":
        form = forms.AddRecipeToListForm(request.POST)
        
        if form.is_valid():
            recipe = form.cleaned_data['recipe_name']
            
            if Recipe.objects.filter(name=recipe).exists():
                
                # probably a good idea to ask the user if they want to do this
                if not grocery_list.recipes.filter(name=recipe).exists():
                    grocery_list.recipes.add(Recipe.objects.get(name=recipe))
                
                # this too maybe? do we want to add the entire quantity that the recipe
                # calls for, or just the difference between that and what's already
                # on the user's grocery list?
                for food_item in Recipe.objects.get(name=recipe).fooditems.all():
                    
                    if grocery_list.fooditems.filter(name=food_item).exists():
                        grocery_list.fooditems.filter(name=food_item).update(quantity = F('quantity') + food_item.quantity)
                        
                    else:
                        new_food = FoodItem(name=food_item, quantity = food_item.quantity, date=timezone.now())
                        new_food.save()
                        grocery_list.fooditems.add(new_food)
                                
                messages.warning(request, "Grocery list items updated")
                

#                # probably a good idea to ask the user if they want to do this
#                if grocery_list.recipes.filter(name=recipe).exists():
#                    
#                    for food_item in Recipe.objects.filter(name=recipe):
#                        on_hand = grocery_list.fooditems.get(name=food_item.name).quantity()
#                        if on_hand < food_item.quantity:
#                            diff = food_item.quantity - on_hand
#                            grocery_list.fooditems.filter(name=food_item).update(quantity = F('quantity') + diff)
#                                
#                    messages.warning(request, "Grocery list items updated")
#    
#                else:
#                    # have to use .get() instead of .filter() ??? something about QuerySets
#                    grocery_list.recipes.add(Recipe.objects.get(name=recipe))
            
            else:
                new_recipe = Recipe(name=recipe, date=timezone.now())
                new_recipe.save()
                grocery_list.recipes.add(new_recipe)
            
        return HttpResponseRedirect(reverse('groceryList:detail', args = (pk,)))
            

    else:
        form = forms.AddRecipeToListForm()
    
    return render(request, 'groceryList/detail.html', {'form': form})

def add_to_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk = pk)
    
    if request.method == "POST":
        form = forms.AddItemToRecipeForm(request.POST)
        
        if form.is_valid():
            food = form.cleaned_data['food_item']

            if FoodItem.objects.filter(name=food).exists():

                # probably a good idea to ask the user if they want to do this
                if recipe.fooditems.filter(name=food).exists():
                    recipe.fooditems.filter(name=food).update(quantity = F('quantity') + 1)
    
                else:            
                    recipe.fooditems.add(FoodItem.objects.filter(name=food))
            
            else:
                new_food = FoodItem(name=food, date=timezone.now())
                new_food.save()
                recipe.fooditems.add(new_food)
            
        return HttpResponseRedirect(reverse('groceryList:recipe', args = (pk,)))
            

    else:
        form = forms.AddItemToListForm()
    
    return render(request, 'groceryList/recipe.html', {'form': form})
