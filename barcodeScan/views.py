import requests
import json
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import BarcodeForm
from django.db.models import F
from inventory.views import add as inv_add
from groceryList.models import GroceryList, GroceryItems


# initial view - prompt for barcode / do processing
def index(request):
    # if the method is POST, do some processing
    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            # fetch the JSON file from the external API & convert to py dictionary
            barcode = (form.cleaned_data['barcode'])
            url = 'http://world.openfoodfacts.org/api/v0/product/%s.json' % barcode
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
            context.update({'all_grocery_lists': GroceryList.objects.filter(user=request.user)})
            # add the barcode
            context.update({'barcode': barcode})

            # display the HTML page, passing the template context generated above
            return render(request, 'barcodeScan/confirm.html', context)
    else:
        # otherwise if GET, then just display a blank form
        form = BarcodeForm()

    return render(request, 'barcodeScan/index.html', {'form': form})


# when a user wants to add an item to a grocery list, go here
def add_to_list(request, barcode):
    # if the method is POST, do some processing
    if request.method == "POST":
        # TODO - add some sort of a one-time token to verify that this POST is coming from a legitimate user

        # make sure barcode is valid (never trust the evil user)
        if len(barcode) > BarcodeForm().fields['barcode'].max_length:
            raise Http404

        # get the selected grocery list's id
        id = request.POST['selected_grocery_list']
        # get the grocery list that was selected from the form
        grocery_list = get_object_or_404(GroceryList, pk=id, user=request.user)
        grocery_items = GroceryItems.objects.filter(groceryList=grocery_list)

        # get the food's name string from the form
        food = request.POST['food_name']

        # check if item exists already, update quantity accordingly
        if grocery_items.filter(name=food, barcode=barcode).exists():
            # edge case where user confirms an item and rescans it:
            # we don't want the quantity to go off the confirmed amount or else the
            # inventory would grow on the next confirm
            if grocery_items.filter(name=food, barcode=barcode).first().confirmed:
                # reset the grocery item to unconfirmed so user can reconfirm to update
                # inventory. reset to 1 so quantities aren't duplicated
                grocery_items.filter(name=food, barcode=barcode).update(quantity=1, confirmed=False)
            else:
                grocery_items.filter(name=food, barcode=barcode).update(quantity=F('quantity') + 1)
        else:
            # add new GroceryItem to the grocery list
            GroceryItems.objects.create(
                groceryList=grocery_list,
                name=food,
                quantity=1,
                barcode=barcode,
                date=timezone.now(),
                inventoryItem=None)

        # take the user to the groceryList to see their added item
        return HttpResponseRedirect(reverse('groceryList:detail', args=(id,)))
    else:
        # we should never receive a GET request to this view's URL
        raise Http404


# when a user wants to add an item to their inventory, go here
def add_to_inventory(request, barcode):
    # if the method is POST, do some processing
    if request.method == "POST":

        # make sure barcode is valid (never trust the evil user)
        if len(barcode) > BarcodeForm().fields['barcode'].max_length:
            raise Http404

        # get the food's name string from the form
        food = request.POST['food_name']

        # no food name? nothing to do here
        if not food:
            return

        # add the item to the inventory db
        inv_add(request, food, barcode)

        # take the user to their inventory to see their added item
        return HttpResponseRedirect(reverse('inventory:index'))
    else:
        # we should never receive a GET request to this view's URL
        raise Http404
