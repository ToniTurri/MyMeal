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

'''
Need to save the last date person consumed something, or accessed stats
class Time_Stamp(models.Model):
    time = models.TimeField(default = datetime.now())

'''
