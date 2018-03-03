import requests
import json
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .forms import BarcodeForm

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
			context = {'generic_name': json_data.get('product').get('generic_name')}
			context.update({'product_name_en': json_data.get('product').get("product_name_en")})
			context.update({'image_front_url': json_data.get('product').get("image_front_url")})

			# display the HTML page, passing the template context generated above
			return render(request, 'barcodeScan/confirm.html', context)

	else:
		# otherwise if GET, then just display a blank form
		form = BarcodeForm()
	return render(request, 'barcodeScan/index.html', {'form': form})

# when a user wants to add an item to a grocery list, go here
def confirm(request):
	# for now, simply returns to index; TODO: integrate with the groceryList models and add item name to DB
	return HttpResponseRedirect(reverse('barcodeScan:index'))