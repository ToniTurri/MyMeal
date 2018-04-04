import requests
import json
from django.http import Http404
from django.shortcuts import render

# initial view & search results
def index(request):
	# if the method is POST, do some processing
	if request.method == 'POST':
		# populate our context with the json response data
		context = get_search_results(request)
		# make sure that matches were found
		if context is None:
			return render(request, 'recipeFinder/not_found.html')
		# display the data as results
		return render(request, 'recipeFinder/results.html', context)

	# method is GET
	# otherwise it's a fresh new search - clear the previous results
	if 'matches' in request.session:
		request.session.pop('matches')
	return render(request, 'recipeFinder/index.html')

# recipe detail view
def recipe_detail(request, id):
	# if the method is GET, do some processing
	if request.method == 'GET':
		# populate our context with the json response data
		context = get_recipe_details(id)
		# in case something went wrong
		if context is None:
			return render(request, 'recipeFinder/not_found.html')

		context.update({'matches': request.session.get('matches')})
		# display the data as results
		return render(request, 'recipeFinder/detail.html', context)
	else:
		# we should never receive a GET request to this view's URL
		raise Http404

# get search data from the Yummly json response and return it
def get_search_results(request):
	# if we already did a search, use those results
	if (request.session.get('matches')):
		context = {'matches': request.session.get('matches')}
		return context

	# otherwise, perform API lookup (for now, load our mock search result)
	with open('search-sample.json') as json_data:
		results = json.load(json_data)

	# return None if no matches found
	if not results.get('totalMatchCount'):
		return None

	# return None if for whatever reason the response json is empty
	if not results:
		return None

	# else, populate context with whatever data we wish to display
	context = {}
	matches = results.get('matches')
	context.update({'criteria': results.get('criteria')})
	context.update({'matches': matches})
	# remember the search results in our session
	request.session['matches'] = matches
	return context

# get recipe data from the Yummly json response and return it
def get_recipe_details(id):
	# perform API lookup on id (for now, load our mock recipe detail)
	with open('recipe-sample.json') as json_data:
		results = json.load(json_data)

	# return None if for whatever reason the response json is empty
	if not results:
		return None

	# else, populate context with whatever data we wish to display
	context = results

	return context