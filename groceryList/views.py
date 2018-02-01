from django.http import HttpResponse
from groceryList.models import GroceryList
import datetime

def index(request):
	b = GroceryList(name='Toni Food',date=datetime.datetime.now())
	b.save()

	return HttpResponse("Hello, world. You're at the polls index.")