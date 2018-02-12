from .models import GroceryList #, FoodItem
from .forms import AddListForm, AddItemToListForm

#from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages

class IndexView(generic.ListView):
    # template_name attribute used to tell Django to use /groceryList/index.html 
    # instead of the default template name <app name>/<model name>_detail.html
    template_name = 'groceryList/index.html'
    context_object_name = 'recently_added'
    
    def get_queryset(self):
        # Display all grocery lists
        return GroceryList.objects.all()
    
class DetailView(generic.DetailView):
    model = GroceryList
    template_name = 'groceryList/detail.html'
    
def create(request):
    return render(request, 'groceryList/new.html')

def add(request):
    if request.method == "POST":
        form = AddListForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['name']
            if GroceryList.objects.filter(name=text).exists():
                return render(request, 'groceryList/new.html', {
                        'error_message': "Grocery list already exists", })
            else:
                time = timezone.now()                
                GroceryList.objects.create(name=text, date=time)
                return HttpResponseRedirect(reverse('groceryList:index'))
    # if method = GET, then return a blank form
    else:
        form = AddListForm()
    return render(request, 'groceryList:index', {'form':form})

def new(request): 
    return render(request, 'groceryList/new.html')

def add_to_list(request, list_id):
    grocery_list = get_object_or_404(GroceryList, pk = list_id)
    
    if request.method == "POST":
        form = AddItemToListForm(request.POST)
        
        if form.is_valid():
            food = form.cleaned_data['food_item']
            
            if grocery_list.fooditem_set.filter(name=food).exists():
                messages.success(request, "That item is already on your grocery list")
                
                return HttpResponseRedirect(reverse('groceryList:detail', args = (list_id,)))

            else:
                time = timezone.now()                
                grocery_list.fooditem_set.create(name=food, date=time)

                return HttpResponseRedirect(reverse('groceryList:detail', args = (list_id,)))
    # if method = GET, then return a blank form
    else:
        form = AddItemToListForm()
    
    return render(request, 'groceryList:detail', {'form':form})