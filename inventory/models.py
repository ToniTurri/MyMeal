from django.db import models
from django.contrib.auth.models import User

class InventoryItem(models.Model):
	user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
	name = models.CharField(max_length = 100)
	quantity = models.IntegerField(default=1)
	barcode = models.CharField(max_length=13, blank=True)
	date = models.DateTimeField(null=True, blank=True)

	def __str__(self):
	    return self.name
