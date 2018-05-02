import requests
import json
import string
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.shortcuts import render
from inventory.models import InventoryItem
from recipes.models import Recipe, RecipeIngredients
from stats.models import Consumed_Stats
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from .forms import IngredientInputForm

app_id = '6fd6322a'
api_key = '3ea09467f568742e613075b1305e2eb2'

# set to True to use mock JSON files instead of API query
DEBUGGING = False

# initial view & search results
def index(request):
	# method is POST
	# go back to previous search results
	if request.method == 'POST':
		ingredients = request.session.get('ingredients')
		search_phrase = request.session.get('search_phrase')
		context = get_search_results(request, ingredients, search_phrase)

		# make sure that matches were found
		if context is None:
			return render(request, 'recipeFinder/not_found.html')

		return render(request, 'recipeFinder/results.html', context)
	else:
		# method is GET
		# it's a fresh new search - clear the previous results held in session
		if 'matches' in request.session:
			request.session.pop('matches')
		if 'ingredients' in request.session:
			request.session.pop('ingredients')
		if 'search_phrase' in request.session:
			request.session.pop('search_phrase')
		return render(request, 'recipeFinder/index.html')

# recipe detail view
def recipe_detail(request, id, course=None):
	# if the method is POST, then try and save the recipe
	if request.method == 'POST':
		# get the old recipe context
		context = request.session.get('recipe_context')
		is_saved = context.get('is_saved')

		if not is_saved:
			# try to save the recipe
			if save_recipe(request, context):
				# all good
				print("Successfully saved recipe %s" % id)
			else:
				# something went wrong!
				print("Problem saving recipe %s" % id)
		else:
			Recipe.objects.filter(yummlyId = id).delete()
			print("Removed recipe %s" % id)

		# update save button
		context.update({'is_saved': Recipe.objects.filter(yummlyId = id).exists()})
		request.session.update({'recipe_context': context})

		return render(request, 'recipeFinder/detail.html', context)
	else:
		# if the method is GET, display recipe details

		# populate our context with the json response data
		context = get_recipe_details(id)

		# in case something went wrong
		if context is None:
			return render(request, 'recipeFinder/not_found.html')

		# if the recipe is saved, add that to the context (for save button)
		context.update({'is_saved': Recipe.objects.filter(yummlyId = id).exists()})
		context.update({'course': course})

		# save the current context
		request.session['recipe_context'] = context
		# display the data as results
		return render(request, 'recipeFinder/detail.html', context)

# get search data from the Yummly json response and return it
def get_search_results(request, ingredients, search_phrase):
	# if we already did a search, use those results
	if (request.session.get('matches')):
		context = {'matches': request.session.get('matches')}
		return context

	# otherwise, perform API lookup
	# use JSON mock if DEBUGGING is True
	if DEBUGGING:
		with open('search-sample.json') as json_data:
			results = json.load(json_data)
	else:
		url = 'http://api.yummly.com/v1/api/recipes?&q='
		url += search_phrase

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
	request.session['ingredients'] = ingredients
	request.session['search_phrase'] = search_phrase
	return context

# get recipe data from the Yummly json response and return it
def get_recipe_details(id):
	# perform API lookup on id
	if DEBUGGING:
		with open('recipe-sample.json') as json_data:
			results = json.load(json_data)
	else:
		url = 'https://api.yummly.com/v1/api/recipe/%s' % id
		results = query_API(url)

	# return None if for whatever reason the response json is empty
	if not results:
		return None

	# else, populate context with whatever data we wish to display
	context = results

	return context

# try to save the recipe to the recipes app
def save_recipe(request, context):

	yummlyId = context.get('id')
	name = context.get('name')
	prepTime = context.get('totalTime')
	ingredients = context.get('ingredientLines')
	instructions = '' # no instructions from Yummly

	# get the images if there are any
	images = context.get('images')

	# try to get the large url first, then the small if none available
	if(images[0]):
		image = images[0].get('hostedLargeUrl')

		if not image:
			image = images[0].get('hostedSmallUrl')

	# yield is a string
	servingsString = context.get('yield')

	# try to get external url
	source = context.get('source')
	if source:
		externalLink = source.get('sourceRecipeUrl')

	# try to get the category
	category = context.get('course')
	if not category:
		category = None

	# add other fields
	new_recipe = Recipe.objects.create(
		name=name,
		date=timezone.now(),
		prepTime=prepTime,
		servings=servingsString,
		category=category,
		instructions=instructions,
		externalLink=externalLink,
		yummlyId = yummlyId,
		imageUrl=image)

	# Save ingredients for each form in the formset
	new_ingredients = []

	for ingredient in ingredients:
		inventoryItem = findInventoryItem(ingredient)
		if ingredient:
			new_ingredient_link = RecipeIngredients(
				recipe=new_recipe,
				ingredient=ingredient,
				inventoryItem=inventoryItem
				)
			new_ingredients.append(new_ingredient_link)

	try:
		with transaction.atomic():
			RecipeIngredients.objects.bulk_create(new_ingredients)
			return True
	except IntegrityError:
		return False

# perform some NLP on the ingredient line and then check against database to see if it
# contains any InventoryItems
# return the first one found, or None
def findInventoryItem(ingredientLine):
	# try to clean the ingredient line of garbage before running the query
	ingredientLine = cleanIngredientLine(ingredientLine)

	# check cleaned string for a match in the InventoryItem db
	inventoryItems = None
	try:
		if not inventoryItems:
			inventoryItems = InventoryItem.objects.raw("SELECT * FROM inventory_inventoryitem "
													   "WHERE %s LIKE '%%' || name || '%%'", [ingredientLine])
	except InventoryItem.DoesNotExist:
		if not inventoryItems:
			inventoryItems = None

	# return the first match--or if none found, return None
	return first(inventoryItems) if inventoryItems else inventoryItems;

# safely get the first element of a raw query set
def first(rawquery):
	try:
		return rawquery[0]
	except:
		return None

def cleanIngredientLine(ingredientLine):
	# filter out punctuation
	ingredientLine = re.sub('['+string.punctuation+']', '', ingredientLine)
	# filter out special characters
	ingredientLine = re.sub('\W+', ' ', ingredientLine)
	# tokenize
	tokens = word_tokenize(ingredientLine)
	# filter out english stop words ('a', 'is', 'this', 'the', 'each', etc)
	stop_words = set(stopwords.words('english'))
	potentialIngredients = [w for w in tokens if not w in stop_words]
	# put cleaned ingredient string back together
	return ' '.join(str(w) for w in potentialIngredients)

def query_API(url):
	headers = {'X-Yummly-App-ID': app_id,
			   'X-Yummly-App-Key': api_key}
	response = requests.get(url, headers=headers)
	try:
		return json.loads(response.text)
	except ValueError:
		return None

# Shows inventory with checkboxes to select ingredients
def inventoryCheck(request):
	if request.method == 'GET' :
		inventory_items = InventoryItem.objects.all()
		context = {'inventory_items': inventory_items}
		return render(request, 'recipeFinder/inventory-check.html', context)

	# This isn't supposed to actually do anything, but this is where the data is
	if request.method == 'POST':
		ingredients = request.POST.getlist('checked')
		search_phrase = ''
		# populate our context with the json response data
		context = get_search_results(request, ingredients, search_phrase)
		# make sure that matches were found
		if context is None:
			return render(request, 'recipeFinder/not_found.html')
		# display the data as results
		return render(request, 'recipeFinder/results.html', context)

# Almsot there
def freeSelect(request):

	IngredientFormSet = formset_factory(IngredientInputForm, max_num=20, min_num=1, validate_min=True, extra=0)
	if request.method == 'POST':
		ingredient_formset = IngredientFormSet(request.POST)
		if ingredient_formset.is_valid():

			ingredients = []

			for ingredient_form in ingredient_formset:
				ingredient = ingredient_form.cleaned_data.get('item')
				# make sure it's not empty
				if ingredient:
					ingredients.append(ingredient)

			search_phrase = ''
			context = get_search_results(request, ingredients, search_phrase)
			if context is None:
				return render(request, 'recipeFinder/not_found.html')

			return render(request, 'recipeFinder/results.html', context)

	else:
		ingredient_formset = IngredientFormSet()
		context = {'ingredient_formset': ingredient_formset}
		return render(request, 'recipeFinder/free-select.html', context)


#
def suggestions(request):
	stats_list = Consumed_Stats.objects.order_by('-total')
	search_phrase = '' # temp test phrase until better thing comes

	# get number of ingredients to use ( might need work)
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
		ingredients = ingredients[:-1]
		count -=1

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
