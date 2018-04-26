from django.db import models
from groceryList.models import FoodItem

# Create your models here.

class Consumed_Stats(models.Model):
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    count1 = models.IntegerField(default = 1) # Most recent day
    count2 = models.IntegerField(default = 0)
    count3 = models.IntegerField(default = 0)
    count4 = models.IntegerField(default = 0)
