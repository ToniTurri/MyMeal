# Generated by Django 2.0.2 on 2018-04-24 22:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipe_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipeingredients',
            old_name='foodItemId',
            new_name='foodItem',
        ),
        migrations.RenameField(
            model_name='recipeingredients',
            old_name='recipeId',
            new_name='recipe',
        ),
    ]