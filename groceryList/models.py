from django.db import models

class GroceryList(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
    	return self.name

class GroceryListItems(models.Model):
	groceryListId = models.IntegerField()
	foodItemId = models.IntegerField()
	quantity = models.IntegerField()

	def __str__(self):
		return self.name