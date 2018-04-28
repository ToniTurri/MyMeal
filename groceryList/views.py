from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.utils import timezone
from django.contrib import messages
from django.db.models import F
from django.views.generic.edit import CreateView
from .models import GroceryList, FoodItem
from . import forms
from stats.models import Consumed_Stats


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

        return context

class GroceryListView(DetailView):
    model = GroceryList
    template_name = 'groceryList/detail.html'

    def get_context_data(self, **kwargs):
        context = super(GroceryListView, self).get_context_data(**kwargs)
        context['item_form'] = forms.AddItemToListForm
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

            if GroceryList.objects.filter(name=text).exists():
                messages.warning(request, "Grocery list already exists")

                return HttpResponseRedirect(reverse('groceryList:new'))

            # redirect to new grocery list after creation
            else:
                new_list = GroceryList.objects.create(name=text, date=timezone.now())

                # *if we are making a list from the barcodeScan app, add the food item too
                if scanned_food_name is not None:
                    new_food = FoodItem(name=scanned_food_name, date=timezone.now())
                    new_food.save()
                    new_list.fooditems.add(new_food)

                return HttpResponseRedirect(reverse('groceryList:detail', args = (new_list.id,)))

    # if method = GET, then return a blank form
    else:
        form = forms.AddGroceryListForm()
    return render(request, 'groceryList:index', {'form':form})

def add_to_list(request, pk):
    grocery_list = get_object_or_404(GroceryList, pk = pk)

    if request.method == "POST":
        form = forms.AddItemToListForm(request.POST)

        if form.is_valid():
            food = form.cleaned_data['food_item']
            qty = form.cleaned_data['quantity']

            # probably a good idea to ask the user if they want to do this
            if grocery_list.fooditems.filter(name=food).exists():
                grocery_list.fooditems.filter(name=food).update(quantity = F('quantity') + qty)
            else:
                new_food = FoodItem(name=food, quantity = qty, date=timezone.now())
                new_food.save()
                grocery_list.fooditems.add(new_food)

        return HttpResponseRedirect(reverse('groceryList:detail', args = (pk,)))


    else:
        form = forms.AddItemToListForm()

    return render(request, 'groceryList/detail.html', {'form': form})

def increment_food_item(request):
    pk = None
    if request.method == 'GET':
        pk = request.GET['list_id']
        food_item = request.GET['food_item']

    if pk:
        grocery_list = get_object_or_404(GroceryList, pk = pk)
        qty = grocery_list.fooditems.get(name=food_item).quantity
        grocery_list.fooditems.filter(name=food_item).update(quantity = F('quantity') + 1)

        return HttpResponse(qty + 1)
    return HttpResponse(0)

def decrement_food_item(request):
    pk = None
    if request.method == 'GET':
        pk = request.GET['list_id']
        food_item = request.GET['food_item']

    if pk:
        grocery_list = get_object_or_404(GroceryList, pk = pk)
        qty = grocery_list.fooditems.get(name=food_item).quantity

        # this doesn't work; probably tricky to make it happen here
        if qty == 0:
            grocery_list.fooditems.remove(food_item)
            grocery_list.save()

        else:
            grocery_list.fooditems.filter(name=food_item).update(quantity = F('quantity') - 1)

            try:
                food_item = FoodItem.objects.get(name=food_item)
                stat_item = Consumed_Stats.objects.get(food=food_item)
                stat_item.count1 += 1
                stat_item.total += 1
                stat_item.save()
            except Consumed_Stats.DoesNotExist:
                new_stat_item = Consumed_Stats(food = food_item, count1 = 1,
                count2 = 0, count3 = 0, count4 = 0, total = 1)
                new_stat_item.save()

            return HttpResponse(qty - 1)

    return HttpResponse(0)

