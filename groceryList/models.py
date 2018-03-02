from django.db import models
from django.forms import ModelForm
from django.urls import reverse
#from django.utils import timezone
#import datetime

## do you need to forward-define functions/classes in Pyhton? is there
## a way to reference Recipe() inside GroceryList() without this helper?
#class RecipeForward(models.Model):
#    Recipe()

class GroceryList(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)
    
    fooditems = models.ManyToManyField('FoodItem')
    recipes = models.ManyToManyField('Recipe')

    def __str__(self):
    	return self.name
    
    pass

class FoodItem(models.Model):
    name = models.CharField(max_length = 100, blank=True)
    quantity = models.IntegerField(default=1)
    date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class Recipe(models.Model):
    name = models.CharField(max_length=100, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    
    fooditems = models.ManyToManyField(FoodItem)
    
    def __str__(self):
        return self.name
    
    pass