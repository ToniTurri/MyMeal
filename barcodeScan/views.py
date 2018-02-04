import requests
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from .forms import BarcodeForm

def index(request):
	# if the method is POST, do some processing
	if request.method == 'POST':
		form = BarcodeForm(request.POST)
		if form.is_valid():
			# fetch the JSON file from the external API
			url = 'http://world.openfoodfacts.org/api/v0/product/%s.json' % (form.cleaned_data['number'],)
			r = requests.get(url, stream=True)
			response = StreamingHttpResponse(
				(chunk for chunk in r.iter_content(128 * 128)),
				content_type='application/json')
			# for now, just return it--TODO: pick out relevent data from the JSON file & store in data structures
			return response
	else:
		# otherwise if GET, then just display a blank form
		form = BarcodeForm()
	return render(request, 'barcodeScan/index.html', {'form': form})