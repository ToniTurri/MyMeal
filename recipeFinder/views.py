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
from django.db.models.functions import Lower

app_id = ''
api_key = ''

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
		cleanSearch(request)
		return render(request, 'recipeFinder/index.html')

def cleanSearch(request):
	if 'matches' in request.session:
		request.session.pop('matches')
	if 'ingredients' in request.session:
		request.session.pop('ingredients')
	if 'search_phrase' in request.session:
		request.session.pop('search_phrase')

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
		url = 'https://api.yummly.com/v1/api/recipes?&q=%s' % search_phrase.lower()

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
		yummlyId=yummlyId,
		imageUrl=image)

	# create the RecipeIngredients
	new_ingredients = []

	for ingredient in ingredients:
		# try to automatically link ingredient to inventory item
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
			query = "SELECT * FROM inventory_inventoryitem " \
					"WHERE %s LIKE '%%' || name || '%%'" \
					" ORDER BY LENGTH(name) DESC LIMIT 1"
			inventoryItems = InventoryItem.objects.raw(query, [ingredientLine])
	except InventoryItem.DoesNotExist:
		if not inventoryItems:
			inventoryItems = None

	# return the first match (if none found, first() returns None)
	return first(inventoryItems)

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

	cleanSearch(request)

	if request.method == 'GET' :
		inventory_items = InventoryItem.objects.values_list('name', flat=True).distinct()
		search_saved = False
		context = {'inventory_items': inventory_items,
				    'search_saved':search_saved}
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

	cleanSearch(request)

	IngredientFormSet = formset_factory(IngredientInputForm, max_num=20, min_num=1, validate_min=True, extra=0)
	if request.method == 'POST':
		ingredient_formset = IngredientFormSet(request.POST)
		if ingredient_formset.is_valid():

			ingredients = []

			for ingredient_form in ingredient_formset:
				ingredient = ingredient_form.cleaned_data.get('item')
				# make sure it's not empty
				if ingredient:
					ingredients.append(ingredient.lower())

			search_phrase = ''
			context = get_search_results(request, ingredients, search_phrase)
			if context is None:
				return render(request, 'recipeFinder/not_found.html')

			return render(request, 'recipeFinder/results.html', context)

	else:
		ingredient_formset = IngredientFormSet()
		context = {'ingredient_formset': ingredient_formset}
		return render(request, 'recipeFinder/free-select.html', context)


# Suggestions based on stats
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

def searchSaved(request):
	cleanSearch(request)

	if request.method == "POST":
		ingredients = request.POST.getlist('checked')
		recipes = [] # recipes that will be displayed
		test_recipes = [] # start of recipes to see if valid recipe to add
		firstRound = True # check to add to test_recipes or recipes

		# go through the desired ingredients
		for ingredient in ingredients:
			# get all recipe ingredients connected to that item
			try:
				ingredient = InventoryItem.objects.get(name=ingredient)
			except InventoryItem.DoesNotExist:
				continue

			recipeIngredient = RecipeIngredients.objects.filter(inventoryItem=ingredient)

			# go through all the recipes connected to that item and add it if
			# it is in previous recipes
			for r_i in recipeIngredient:
				recipe = Recipe.objects.filter(Recipe=r_i.recipe)
				if not firstRound:
					if recipe in test_recipes and recipe not in recipes:
						recipes.append(recipe)
				else:
					test_recipes.append(recipe)
			# Narrow the amount of recipes since it's not first round
			if not firstRound:
				test_recipes = list(recipes)
			firstRound = False

		if not recipes:
			return render(request, 'recipeFinder/not_found.html')
		context = {'recipes':recipes}
		return render(request, 'recipeFinder/saved-recipe-search.html', context)
	else:
		inventory_items = InventoryItem.objects.all()
		search_saved = True
		context = {'inventory_items': inventory_items,
					'search_saved':search_saved}
		return render(request, 'recipeFinder/inventory-check.html', context)
