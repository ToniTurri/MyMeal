import requests
import json
from django.http import Http404
from django.shortcuts import render
from groceryList.models import FoodItem
from stats.models import Consumed_Stats
from django.db.models import Count

app_id = ''
api_key = ''

# set to True to use mock JSON files instead of API query
DEBUGGING = False

# initial view & search results
def index(request):
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
def get_search_results(request, ingredients, search_phrase):
	# if we already did a search, use those results
	if (request.session.get('matches')):
		context = {'matches': request.session.get('matches')}
		return context

	# otherwise, perform API lookup
	if DEBUGGING:
		with open('search-sample.json') as json_data:
			results = json.load(json_data)
	else:
		url = 'http://api.yummly.com/v1/api/recipes?&q='

		# append ingredients to search url
		allowed_ingredients = []
		for ingredient in ingredients:
			allowed_ingredients.append('&allowedIngredient[]=%s' % ingredient)

		url += ''.join(allowed_ingredients)

		results = query_API(url)

	# return None if for whatever reason the response json is empty
	if not results:
		return None

	# return None if no matches found
	if not results.get('totalMatchCount'):
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
	# perform API lookup on id
	if DEBUGGING:
		with open('recipe-sample.json') as json_data:
			results = json.load(json_data)
	else:
		url = 'http://api.yummly.com/v1/api/recipe/%s' % id
		results = query_API(url)

	# return None if for whatever reason the response json is empty
	if not results:
		return None

	# else, populate context with whatever data we wish to display
	context = results

	return context

def query_API(url):
	headers = {'X-Yummly-App-ID': app_id,
			   'X-Yummly-App-Key': api_key}
	response = requests.get(url, headers=headers)
	try:
		return json.loads(response.text)
	except ValueError:
		return None

# Added from Finn
def inventoryCheck(request):
	if request.method == 'GET' :
		food_items = FoodItem.objects.all()
		context = {'food_items': food_items}
		return render(request, 'recipeFinder/inventory-check.html', context)

	# This isn't supposed to actually do anything, but this is where the data is
	if request.method == 'POST':
		ingredients = request.POST.getlist('checked')
		search_phrase = 'cookies'
		# populate our context with the json response data
		context = get_search_results(request, ingredients, search_phrase)
		# make sure that matches were found
		if context is None:
			return render(request, 'recipeFinder/not_found.html')
		# display the data as results
		return render(request, 'recipeFinder/results.html', context)

# Not yet implemented, trying to figure out cool form techniques
def freeChoice(request):
	return render(request, 'recipeFinder/freechoice.html')

# probably needs tweaking, need to determine number of items to checked
# and some 'counts' have better results than others
def suggestions(request):
	stats_list = Consumed_Stats.objects.order_by('-total')
	search_phrase = None # temp test phrase until better thing comes

	count = resolveCount(len(stats_list))
	if count is None:
		return render(request, 'recipeFinder/not_found.html')
	# Get top values
	ingredients = []
	for i in range(0, count):
		ingredients.append(stats_list[i].food.name)
	context = None
	# make sure that matches were found and keep trying if not
	while context is None and count >= 2:
		context = get_search_results(request, ingredients, search_phrase)
		count -=1
		ingredients = []
		for i in range(0, count):
			ingredients.append(stats_list[i].food.name)

	if context is None:
		return render(request, 'recipeFinder/not_found.html')
	# display the data as results
	return render(request, 'recipeFinder/results.html', context)

# helper function determines the inital number of ingredients to use
def resolveCount(count):
	# This wants at least 2 ingredients for suggestions, and max 6 (6 might be
	# too much, if it works only 1 random thing)
	if not count >= 2:
		return None
	elif count > 5:
		return 4
	return count
