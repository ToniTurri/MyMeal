from django.db import models
from django.forms import ModelForm, ModelChoiceField
from django.urls import reverse
from inventory.models import InventoryItem
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
#from django.utils import timezone
#import datetime

CATEGORY_CHOICES = (
	('', ''),
    ('Appetizers', 'Appetizers'),
    ('Soups', 'Soups'),
    ('Salads', 'Salads'),
    ('Breads', 'Breads'),
    ('Main Dishes', 'Main Dishes'),
    ('Side Dishes', 'Side Dishes'),
    ('Desserts', 'Desserts'),
    ('Breakfast and Brunch', 'Breakfast and Brunch'),
    ('Lunch and Snacks', 'Lunch and Snacks'),
    ('Beverages', 'Beverages'),
    ('Cocktails', 'Cocktails'),
    ('Condiments and Sauces', 'Condiments and Sauces'))

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(0, filename) #instance.user.id

class Recipe(models.Model):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        megabyte_limit = 2.0
        if filesize > megabyte_limit*1024*1024:
            raise ValidationError("Max file size is %sMB" % str(megabyte_limit))

    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)
    prepTime = models.CharField(max_length=20, blank=True, null=True)
    servings = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    instructions = models.TextField(blank=True, null=True)
    yummlyId = models.CharField(max_length=100, null=True, blank=True)
    externalLink = models.URLField(max_length=200,null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True, validators=[validate_image])
    imageUrl = models.URLField(max_length=200,null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    pass

class RecipeIngredients(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	ingredient = models.CharField(max_length=100, null=False, blank=False)
	inventoryItem = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
	    return self.name

	pass