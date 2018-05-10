from django.shortcuts import render
from django.http import Http404
from recipes.models import Recipe
from inventory.models import InventoryItem
from groceryList.models import GroceryList

def index(request):
	# if the method is POST, do some processing
	if request.method == 'POST':
		raise Http404
	else:
		recent_recipes = Recipe.objects.filter(user=request.user).order_by('-date')[:5]
		grocery_lists = GroceryList.objects.filter(user=request.user).order_by('-date')
		low_inventory = InventoryItem.objects.filter(user=request.user).order_by('quantity')[:5]
		context = {
			"recent_recipes": recent_recipes,
			"grocery_lists": grocery_lists,
			"low_inventory": low_inventory
		}

	return render(request, 'dashboard/index.html', context)

