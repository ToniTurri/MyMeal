from django.db import models
from django.forms import ModelForm, ModelChoiceField
from django.urls import reverse
from groceryList.models import FoodItem
from django.core.validators import MinValueValidator
#from django.utils import timezone
#import datetime

CATEGORY_CHOICES = (
	('', ''),
    ('breakfast','Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner','Dinner'),
    ('dessert','Dessert'),
    ('snack','Snack'),
    ('other','Other'),
)


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)
    prepTime = models.CharField(max_length=20, blank=True, null=True)
    servings = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='')
    instructions = models.TextField(blank=True, null=True)
    yummlyId = models.IntegerField(null=True, blank = True)
    externalLink = models.URLField(max_length=200,null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    pass

class RecipeIngredients(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	ingredient = models.CharField(max_length=100)
	foodItem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)

	def __str__(self):
	    return self.name

	pass