from django.db import models
from inventory.models import InventoryItem

# Create your models here.

class Consumed_Stats(models.Model):
    food = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    count1 = models.IntegerField(default = 1) # Most recent day
    count2 = models.IntegerField(default = 0)
    count3 = models.IntegerField(default = 0)
    count4 = models.IntegerField(default = 0)
    total = models.IntegerField(default = 1)
