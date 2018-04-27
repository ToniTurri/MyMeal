from django.db import models
from django.forms import ModelForm, ModelChoiceField
from django.urls import reverse
from groceryList.models import FoodItem
from django.core.validators import MinValueValidator
#from django.utils import timezone
#import datetime

CATEGORY_CHOICES = (
	('', ''),
    ('Breakfast','Breakfast'),
    ('Lunch', 'Lunch'),
    ('Dinner','Dinner'),
    ('Dessert','Dessert'),
    ('Snack','Snack'),
    ('Other','Other'),
)

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
    servings = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='')
    instructions = models.TextField(blank=True, null=True)
    yummlyId = models.IntegerField(null=True, blank = True)
    externalLink = models.URLField(max_length=200,null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True, validators=[validate_image])
    
    def __str__(self):
        return self.name
    
    pass

class RecipeIngredients(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	ingredient = models.CharField(max_length=100, null=False, blank=False)
	foodItem = models.ForeignKey(FoodItem, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
	    return self.name

	pass