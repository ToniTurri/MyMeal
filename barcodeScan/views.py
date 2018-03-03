import requests
import json
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import BarcodeForm
from django.db.models import F
from groceryList.models import GroceryList, FoodItem

# initial view - prompt for barcode / do processing
def index(request):
	# if the method is POST, do some processing
	if request.method == 'POST':
		form = BarcodeForm(request.POST)
		if form.is_valid():
			# fetch the JSON file from the external API & convert to py dictionary
			url = 'http://world.openfoodfacts.org/api/v0/product/%s.json' % (form.cleaned_data['number'],)
			response = requests.get(url)
			json_data = json.loads(response.text)

			# make sure that barcode # is in the database
			if not json_data.get('status'):
				return render(request, 'barcodeScan/not_found.html')

			# attempt to get the food's name and an image if available from the json dictionary
			# the 'generic name' is not always available, but give it preference if it is
			generic_name = json_data.get('product').get('generic_name')
			product_name_en = json_data.get('product').get("product_name_en")

			# we have a generic name
			if generic_name:
				context = ({'food_name': generic_name})
			# otherwise just use the english product name, which should always be available
			elif product_name_en:
				context = ({'food_name': json_data.get('product').get("product_name_en")})
			# if for some reason neither of those exist, just treat it as 'not found'
			else:
				return render(request, 'barcodeScan/not_found.html')

			# otherwise we are good, try and get an image url from the json dict
			context.update({'image_front_url': json_data.get('product').get("image_front_url")})
			# add the list of grocery lists
			context.update({'all_grocery_lists' : GroceryList.objects.all()})

			# display the HTML page, passing the template context generated above
			return render(request, 'barcodeScan/confirm.html', context)
	else:
		# otherwise if GET, then just display a blank form
		form = BarcodeForm()

	return render(request, 'barcodeScan/index.html', {'form': form})

# when a user wants to add an item to a grocery list, go here
def add_to_list(request):
	# if the method is POST, do some processing
	if request.method == "POST":
		# TODO - add some sort of a one-time token to verify that this POST is coming from a legitimate user

		# get the selected grocery list's id
		id = request.POST['selected_grocery_list']
		# get the grocery list that was selected from the form
		grocery_list = get_object_or_404(GroceryList, pk=id)
		# get the food's name string from the form
		food = request.POST['food_name']

		# check if item exists already, update quantity accordingly
		if grocery_list.fooditems.filter(name=food).exists():
			grocery_list.fooditems.filter(name=food).update(quantity=F('quantity') + 1)
		else:
			# add new FoodItem to the grocery list
			new_food = FoodItem(name=food, date=timezone.now())
			new_food.save()
			grocery_list.fooditems.add(new_food)

		# take the user to the groceryList to see their added item
		return HttpResponseRedirect(reverse('groceryList:detail', args=(id,)))
	else:
		# we should never receive a GET request to this view's URL
		raise Http404
