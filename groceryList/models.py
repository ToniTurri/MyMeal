from django.db import models

class GroceryList(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
    	return self.name
    
    pass

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    date = models.DateTimeField(null=True, blank=True)
    
    lists = models.ManyToManyField(GroceryList)
    
    def __str__(self):
        return self.name
    
#	groceryListId = models.IntegerField()
#	foodItemId = models.IntegerField()
#	quantity = models.IntegerField()