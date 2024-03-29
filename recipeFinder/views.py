import requests
import json
import string
import re
import nltk
import random

nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.shortcuts import render
from inventory.models import InventoryItem
from recipes.models import Recipe, RecipeIngredients
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.forms.formsets import formset_factory
from .forms import IngredientInputForm
from inventory.views import generic_foods

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
        return recipe_search(request)


def recipe_search(request):
    cleanSearch(request)
    IngredientFormSet = formset_factory(IngredientInputForm, max_num=20, min_num=1, validate_min=True, extra=0)

    if request.method == 'GET':
        ingredient_formset = IngredientFormSet()
        inventory_items = InventoryItem.objects.filter(user=request.user).values_list('name', flat=True).distinct()
        context = {'ingredient_formset': ingredient_formset,
                   'inventory_items': inventory_items,
                   'food_suggestions': generic_foods + \
                                       [x for x in list(InventoryItem.objects.filter(user=request.user)
                                                        .values_list('name', flat=True).distinct())
                                        if x not in generic_foods]
                   }

        return render(request, 'recipeFinder/recipe_search.html', context)

    # Request is POST, process the form and return search results
    if request.method == 'POST':
        ingredients = request.POST.getlist('checked')
        search_phrase = request.POST.get('search_phrase')
        ingredient_formset = IngredientFormSet(request.POST)

        for ingredient_form in ingredient_formset:
            if ingredient_form.is_valid():
                ingredient = ingredient_form.cleaned_data.get('item')

                # make sure it's not empty
                if ingredient:
                    # make lowercase if it's generic
                    if ingredient.lower() in generic_foods:
                        ingredient = ingredient.lower()
                    ingredients.append(ingredient)

    context = get_search_results(request, ingredients, search_phrase)

    if context is None:
        return render(request, 'recipeFinder/not_found.html')

    return render(request, 'recipeFinder/results.html', context)


# Suggestions based on stats
def suggestions(request):
    # there's probably a way of doing this that will return the maximum (or at least a large)
    # number of recipe matches; as it stands right now, this will return a single match
    if request.method == 'GET':
        cleanSearch(request)

    inventory_items = list(InventoryItem.objects.filter(user=request.user)
                           .values_list('name', flat=True).distinct())
    search_phrase = ''
    n = len(inventory_items)

    # if the user has too few ingredients, don't bother searching. this number could
    # probably be bigger. it isn't strictly necessarily, but if the only thing in their
    # inventory is eggs, whatever results it returns aren't going to be helpful
    if (n < 3):
        context = {'too_few': True}
        return render(request, 'recipeFinder/not_found.html', context)

    context = None
    tries = 0
    while (context is None and tries < 20):
        tries += 1

        # continually sample three random items from the user's inventory until
        # get_search_results returns something valid, or the iteration limit is reached
        index = random.sample(range(0, n), 3)
        ingredients = []

        for i in index:
            ingredients.append(inventory_items[i])

        context = get_search_results(request, ingredients, search_phrase)

    # if the search hasn't returned anything in 20 tries, the user probably only has
    # a handfull of ingredients that aren't typically used together
    if (context is None):
        context = {'too_few': True}
        return render(request, 'recipeFinder/not_found.html', context)

    ## need this to tell /results.html whether or not it's displaying randomly
    ## generated recipes & give the user the option to search again
    context.update({'suggested': True})
    return render(request, 'recipeFinder/results.html', context)


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
            Recipe.objects.filter(yummlyId=id).delete()
            print("Removed recipe %s" % id)

        # update save button
        context.update({'is_saved': Recipe.objects.filter(user=request.user, yummlyId=id).exists()})
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
        context.update({'is_saved': Recipe.objects.filter(user=request.user, yummlyId=id).exists()})
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
        print(url)
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
    instructions = ''  # no instructions from Yummly

    # get the images if there are any
    images = context.get('images')

    # try to get the large url first, then the small if none available
    if (images[0]):
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
        user=request.user,
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
        inventoryItem = find_InventoryItem(ingredient, request.user)
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
def find_InventoryItem(ingredientLine, user):
    # try to clean the ingredient line of garbage before running the query
    ingredientLine = clean_ingredientLine(ingredientLine)

    # check cleaned string for a match in the InventoryItem db
    inventoryItems = None
    if not inventoryItems:
        # first, try query as is--case sensitive for brands
        # (e.g. Cento Crushed Tomatoes has precedence over 'tomatoes')
        query = "SELECT * FROM inventory_inventoryitem " \
                "WHERE %s LIKE '%%' || name || '%%'" \
                "AND user = %s " \
                " ORDER BY LENGTH(name) DESC LIMIT 1"
        inventoryItems = InventoryItem.objects.raw(query, [ingredientLine])
    if not first(inventoryItems):
        # no brand found? try another query, this time lowercasing generic food items
        # (e.g. Tomatoes->tomatoes)
        tokens = word_tokenize(ingredientLine)
        potentialIngredients = [w.lower() for w in tokens if w.lower() in generic_foods]
        ingredientLine = ' '.join(str(w) for w in potentialIngredients)
        query = "SELECT * FROM inventory_inventoryitem " \
                "WHERE %s LIKE '%%' || name || '%%'" \
                "AND user = %s " \
                "ORDER BY LENGTH(name) DESC LIMIT 1"
        inventoryItems = InventoryItem.objects.raw(query, [ingredientLine, user])

    # return the first match (if none found, first() returns None)
    return first(inventoryItems)


# perform some NLP on the ingredient line and then check against generic foods list to see if
# it contains a generic food item
def find_generic_item(ingredientLine):
    # try to clean the ingredient line of garbage before running the query
    ingredientLine = clean_ingredientLine(ingredientLine)
    generic_food = ''
    # sort generic foods by length
    sorted_generic_foods = sorted(generic_foods, key=len)
    for food in sorted_generic_foods:
        if food.lower() in ingredientLine.lower():
            generic_food = food
    # return the last (longest) generic food found, or ''
    return generic_food


# safely get the first element of a raw query set
def first(rawquery):
    try:
        return rawquery[0]
    except:
        return None


def clean_ingredientLine(ingredientLine):
    # filter out punctuation (except apostrophes)
    ingredientLine = re.sub('[' + string.punctuation.replace("'", "") + ']', '', ingredientLine)
    # filter out special characters
    ingredientLine = re.sub("(?=.*\W)^(\w')+$", ' ', ingredientLine)
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


# pop off session variables so that we can start with a fresh, new search
def cleanSearch(request):
    if 'matches' in request.session:
        request.session.pop('matches')
    if 'ingredients' in request.session:
        request.session.pop('ingredients')
    if 'search_phrase' in request.session:
        request.session.pop('search_phrase')


# helper function determines the inital number of ingredients to use
def resolveCount(count):
    # This wants at least 2 ingredients for suggestions, and max 6 (6 might be
    # too much, if it works only 1 random thing)
    if not count >= 2:
        return None
    elif count > 5:
        return 4
    return count
