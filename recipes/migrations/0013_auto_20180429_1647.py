# Generated by Django 2.0.4 on 2018-04-29 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('recipes', '0012_merge_20180429_1625'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipeingredients',
            name='foodItem',
        ),
        migrations.AddField(
            model_name='recipeingredients',
            name='inventoryItem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryItem'),
        ),
    ]
