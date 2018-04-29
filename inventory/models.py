from django.db import models

class InventoryItem(models.Model):
    name = models.CharField(max_length = 100)
    quantity = models.IntegerField(default=1)
    date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name