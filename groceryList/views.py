from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.utils import timezone
from django.contrib import messages
from django.db.models import F
from django.views.generic.edit import CreateView
from . import forms
from recipes.models import Recipe, RecipeIngredients
from inventory.models import InventoryItem
from inventory.views import generic_foods
from inventory.views import add as add_to_inventory
from inventory.views import update as update_inventory
from groceryList.models import GroceryItems, GroceryList
from django.forms.formsets import formset_factory


#from django.contrib.auth.decorators import login_required
#@login_required(login_url='/accounts/login/')
class IndexView(ListView):
    model = GroceryList
    template_name = 'groceryList/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['all_grocery_lists'] = GroceryList.objects.all()
        return context

class NewGroceryListView(CreateView):
    model = GroceryList
    template_name = 'groceryList/new.html'
    form_class = forms.AddGroceryListForm

    def get_context_data(self, **kwargs):
        context = super(NewGroceryListView, self).get_context_data(**kwargs)
        context['food_name'] = self.kwargs.get("food_name")
        context['barcode'] = self.kwargs.get("barcode")

        return context

class GroceryListView(DetailView):
    model = GroceryList
    template_name = 'groceryList/detail.html'

    def get_context_data(self, **kwargs):
        context = super(GroceryListView, self).get_context_data(**kwargs)
        context['item_form'] = forms.AddItemToListForm
        context['grocery_list'] = self.get_object()
        context['grocery_items'] = GroceryItems.objects.filter(groceryList=self.kwargs.get('pk'))
        context['food_suggestions'] = generic_foods + \
                                      [x for x in list(InventoryItem.objects.values_list('name', flat=True).distinct())
                                       if x not in generic_foods]
        return context

def add(request):
    if request.method == "POST":
        form = forms.AddGroceryListForm(request.POST)

        if form.is_valid():
            text = form.cleaned_data['name']

            # *for the special case of scanning an item when there are no lists--
            # create a new list from the barcodeScan app and add the scanned item
            # to it automatically.
            scanned_food_name = request.POST.get("food_name")
            scanned_food_barcode = request.POST.get("barcode")

            if GroceryList.objects.filter(name=text).exists():
                messages.warning(request, "Grocery list already exists")

                return HttpResponseRedirect(reverse('groceryList:new'))

            # redirect to new grocery list after creation
            else:
                new_list = GroceryList.objects.create(name=text, date=timezone.now())

                # *if we are making a list from the barcodeScan app, add the food item too
                if scanned_food_name is not None:
                    new_food = GroceryItems(groceryList=new_list, name=scanned_food_name,
                                            barcode=scanned_food_barcode, date=timezone.now())
                    new_food.save()

                return HttpResponseRedirect(reverse('groceryList:detail', args = (new_list.id,)))

    # if method = GET, then return a blank form
    else:
        form = forms.AddGroceryListForm()
    return render(request, 'groceryList:index', {'form':form})
 
def update(request, pk):

    form = forms.AddItemToListForm()
    grocery_list = get_object_or_404(GroceryList, pk = pk)
    grocery_items = GroceryItems.objects.filter(groceryList=grocery_list)

    if request.method == "POST":        
        form = forms.AddItemToListForm(request.POST)

        if form.is_valid():
            item = form.cleaned_data['name']
            # lowercase the name if its a generic food item
            if item.lower() in generic_foods:
                item = item.lower()
            # try and link the ingredient to an inventory item
            try:
                inventory_item = InventoryItem.objects.filter(name=item)[:1].get()
            except InventoryItem.DoesNotExist:
                inventory_item = None
            #inventory_item = form.cleaned_data['inventory_item']
            quantity = form.cleaned_data['quantity']

            # the add new item form is empty, so attempt to update quantities of
            # existing items in the grocery list instead
            if not item and not quantity:
                update_quantities(grocery_items)
            # either item or quantity is empty which is an invalid state for adding 
            # a new item to the list. so show an error to the user
            elif not item or not quantity:
                messages.warning(request, "Item and Quantity are required when adding a new item to the list.")
                return HttpResponseRedirect(reverse('groceryList:detail', args = (grocery_list.id,)))
            # else the user inputted a new grocery item successfully
            # update the quantities as well, since they are considered editable
            # at this point in time too
            else:
                update_quantities(request, grocery_items)
                GroceryItems.objects.create(groceryList=grocery_list, 
                                            name=item, 
                                            quantity=quantity, 
                                            date=timezone.now(),
                                            inventoryItem=inventory_item)

                return HttpResponseRedirect(reverse('groceryList:detail', args = (grocery_list.id,)))

    context = {
        'item_form': form,
        'grocery_list': grocery_list,
        'grocery_items': grocery_items
    }

    return render(request, 'groceryList/detail.html', context)

def update_quantities(request, grocery_items=None):
    if not grocery_items:
        return
    # confirmed items indicate they've already been added to the inventory with
    # their amounts. so we will skip them here
    unconfirmed_grocery_items = (x for x in grocery_items if not x.confirmed)
    for grocery_item in unconfirmed_grocery_items:
        identifier = 'quantity_item_' + str(grocery_item.id)                 
        if identifier in request.POST:
            grocery_item_amount = request.POST[identifier]
            grocery_item.quantity = grocery_item_amount
            grocery_item.save()

def confirm_item(request, pk, id):

    if request.method == 'GET':
        grocery_list = get_object_or_404(GroceryList, pk = pk)
        try:
            grocery_item = GroceryItems.objects.get(pk=id,groceryList=grocery_list,)
        except GroceryItems.DoesNotExist:
            grocery_item = None
        quantity = request.GET['quantity']

        if grocery_list and grocery_item:
            # Update the quantity and set it as confirmed
            # Confirmed indicates that it was added to the inventory either as a new item
            # or the quantity of the inventory item it was linked to gets updated
            grocery_item.quantity = quantity
            grocery_item.confirmed = True
            grocery_item.save()

            if grocery_item.barcode:
                # if the grocery item was linked to an inventory item update that
                # item directly
                if grocery_item.inventoryItem:
                    update_inventory(grocery_item, grocery_item.quantity)
                    # add barcode as well if it the linked item does not have one
                    if not grocery_item.inventoryItem.barcode:
                        grocery_item.inventoryItem.barcode = grocery_item.barcode
                else:
                    # otherwise just add it to the inventory
                    add_to_inventory(grocery_item.name, grocery_item.barcode, grocery_item.quantity)
            else:
                # if the grocery item was linked to an inventory item update that
                # item directly
                if grocery_item.inventoryItem:
                    update_inventory(grocery_item.inventoryItem, grocery_item.quantity)
                else:
                    # otherwise just add it to the inventory
                    add_to_inventory(grocery_item.name, '', grocery_item.quantity)

    return HttpResponseRedirect(reverse('groceryList:detail', args = (grocery_list.id,)))

def delete_list(request, pk):
	if request.method == 'POST':
		GroceryList.objects.filter(id=pk).delete()
		return HttpResponseRedirect(reverse('groceryList:index'))
     
def delete_item(request, pk, id):

    if request.method == 'GET':
        grocery_list = get_object_or_404(GroceryList, pk = pk)
        try:
            grocery_item = GroceryItems.objects.get(pk=id,groceryList=grocery_list)
        except GroceryItems.DoesNotExist:
            grocery_item = None

        if grocery_list and grocery_item:
            grocery_item.delete()

    return HttpResponseRedirect(reverse('groceryList:detail', args = (grocery_list.id,)))