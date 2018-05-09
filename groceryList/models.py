from django.db import models
from django.forms import ModelForm
from django.urls import reverse
from inventory.models import InventoryItem
from django.contrib.auth.models import User

class GroceryList(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
    	return self.name
    
    pass

class GroceryItems(models.Model):
    groceryList = models.ForeignKey(GroceryList, on_delete=models.CASCADE)
    name = models.CharField(max_length = 100, blank=True)
    quantity = models.IntegerField(default=1)
    barcode = models.CharField(max_length=13, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    inventoryItem = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, null=True, blank=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
