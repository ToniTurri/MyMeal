from django.db import models
from inventory.models import InventoryItem
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Consumed_Stats(models.Model):
	user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
	food = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
	count1 = models.IntegerField(default = 1) # Most recent day
	count2 = models.IntegerField(default = 0)
	count3 = models.IntegerField(default = 0)
	count4 = models.IntegerField(default = 0)
	total = models.IntegerField(default = 1)


# Need to save the last date person consumed something, or accessed stats
class Time_Stamp(models.Model):
    time = models.DateTimeField(default=timezone.now)
