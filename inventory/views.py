from django.shortcuts import render, redirect
from django.http import Http404
from inventory.models import InventoryItem
from django.db.models import F
from django.utils import timezone
from django.contrib.auth.decorators import login_required

#@login_required(login_url='/accounts/login/')
def index(request):
	# method is POST
	if request.method == 'POST':
		# no POST requests to this URL
		raise Http404
	else:
		# display the inventory
		context = {'inventoryitems': InventoryItem.objects.all()}
	return render(request, 'inventory/index.html', context)

def add_view(request, name):
	# method is POST
	if request.method == 'POST':
		add(name)
	else:
		# no GET requests to this URL
		raise Http404
	return redirect('inventory:index')

def add(name, barcode=None):
	item = InventoryItem(name=name, quantity=1, barcode=barcode, date=timezone.now())
	existing_item = InventoryItem.objects.filter(name=name, barcode=barcode).first()
	# if the item is in the db already, update its quantity by 1
	if existing_item:
		update(existing_item, 1)
	else:
		item.save()

def remove_view(request, pk):
	# method is POST
	if request.method == 'POST':
		InventoryItem.objects.get(pk=pk).delete()
	else:
		# no GET requests to this URL
		raise Http404
	return redirect('inventory:index')

def update_view(request, pk, quantity):
	# method is POST
	if request.method == 'POST':
		# parse int from the arg string
		quantity = int(quantity)
		# only allowed qty parameters are 1 and -1
		if(quantity != 1 and quantity != -1):
			return redirect('inventory:index')

		# get the item to update
		item = InventoryItem.objects.get(pk=pk)

		# don't decrement if we're already at 0
		if quantity == -1 and item.quantity == 0:
			return redirect('inventory:index')

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