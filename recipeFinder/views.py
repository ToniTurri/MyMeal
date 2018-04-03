import requests
import json
from django.http import Http404
from django.shortcuts import render

# initial view
def index(request):
	# if the method is POST, do some processing
	if request.method == 'POST':
		# populate our context with the json response data
		context = get_results(request)
		# make sure that matches were found
		if context is None:
			return render(request, 'recipeFinder/not_found.html')
		# display the data as results
		return render(request, 'recipeFinder/results.html', context)
	return render(request, 'recipeFinder/index.html')

# get data from the Yummly json response and store return it
def get_results(request):
	# for now, load our mock search result
	with open('recipe-sample.json') as json_data:
		results = json.load(json_data)

	# if the method is POST, do some processing
	if request.method == "POST":
		# return None if no matches found
		if not results.get('totalMatchCount'):
			return None
		# else, populate context with whatever data we wish to display
		context = {}
		context.update({'criteria': results.get('criteria')})
		context.update({'matches': results.get('matches')})
		return context
	else:
		# we should never receive a GET request to this view's URL
		raise Http404
