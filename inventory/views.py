import csv
from django.shortcuts import render, redirect
from django.http import Http404
from inventory.models import InventoryItem
from django.utils import timezone
from inventory.forms import AddItemToInventoryForm
from django.db.models.functions import Lower
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from stats.models import Consumed_Stats
from stats.views import timeCheck

# populate global list of generic food items
generic_foods = []
with open('generic-foods.csv', encoding='utf-8') as csvfile:
    foodreader = csv.reader(csvfile, delimiter=",", quotechar='|')
    for row in foodreader:
        generic_foods.append(''.join(row))


def index(request):
    # method is POST
    if request.method == 'POST':
        # no POST requests to this URL
        raise Http404
    else:
        # alphabetize the inventory items
        inventory_items = InventoryItem.objects.filter(user=request.user).order_by(Lower('name'))

        # set up the first page for pagination
        page = request.GET.get('page', 1)

        # display 10 items per page
        paginator = Paginator(inventory_items, 10)

        try:
            displayed_inv_items = paginator.page(page)
        except PageNotAnInteger:
            displayed_inv_items = paginator.page(1)
        except EmptyPage:
            displayed_inv_items = paginator.page(paginator.num_pages)

        # display the inventory
        context = {
            'add_item_form': AddItemToInventoryForm(),
            'inventoryitems': displayed_inv_items,
            'food_suggestions': generic_foods + \
                                [x for x in list(InventoryItem.objects.filter(user=request.user)
                                                 .values_list('name', flat=True).distinct())
                                 if x not in generic_foods]
        }

    return render(request, 'inventory/index.html', context)


def add_view(request):
    # method is POST
    if request.method == 'POST':
        form = AddItemToInventoryForm(request.POST)
        if form and form.is_valid():
            name = (form.cleaned_data['name'])
            add(request, name)
    else:
        # no GET requests to this URL
        raise Http404
    return redirect('inventory:index')


def add(request, name, barcode='', quantity=1):
    # lowercase the name if its a generic food item
    if name.lower() in generic_foods:
        name = name.lower()
    item = InventoryItem(user=request.user, name=name, quantity=quantity, barcode=barcode, date=timezone.now())
    possible_items = InventoryItem.objects.filter(user=request.user, name=name)
    existing_item = None
    # prefer items with barcodes
    for item in possible_items:
        if item.barcode:
            existing_item = item
    # otherwise it's got no barcode
    if not existing_item:
        existing_item = InventoryItem.objects.filter(user=request.user, name=name).first()
    # if the item is in the db already, update its quantity by 1
    if existing_item:
        # if this item had a barcode and the previous item did not, add the barcode to the previous item
        if not existing_item.barcode and barcode:
            existing_item.barcode = barcode
        update(existing_item, quantity)
    else:
        item.save()


@csrf_exempt
def remove_view(request, pk):
    # method is POST
    if request.method == 'POST':
        try:
            InventoryItem.objects.filter(pk=pk, user=request.user).delete()
        except InventoryItem.DoesNotExist:
            raise Http404
    else:
        # no GET requests to this URL
        raise Http404
    return redirect('inventory:index')


@csrf_exempt
def update_view(request, pk, quantity):
    # method is POST
    if request.method == 'POST':
        # parse int from the arg string
        quantity = int(quantity)

        # get the item to update
        try:
            item = InventoryItem.objects.filter(pk=pk, user=request.user).first()
        except InventoryItem.DoesNotExist:
            item = None

        # something went wrong
        if not item:
            raise Http404

        # we want to distinguish between saving the quantity
        # amount from the inventory view vs updating the
        # quantity from the grocery list view
        if 'inventory-view' in request.POST:
            collect_stats(request, item, quantity)
            # update the qty
            item.quantity = quantity
            item.save()
        else:
            # update the qty
            update(item, quantity)
    else:
        # no GET requests to this URL
        raise Http404
    return redirect('inventory:index')


def update(item, quantity):
    # update the qty
    item.quantity = F('quantity') + quantity
    item.save()


def collect_stats(request, item, quantity):
    # for stats
    if quantity < item.quantity:
        difference = item.quantity - quantity
        timeCheck(request)
        try:
            stat_item = Consumed_Stats.objects.get(food=item)
            stat_item.count1 += difference
            stat_item.total += difference
            stat_item.save()
        except Consumed_Stats.DoesNotExist:
            stat_item = Consumed_Stats(food=item, count1=difference, count2=0,
                                       count3=0, count4=0, total=difference)
            stat_item.save()
