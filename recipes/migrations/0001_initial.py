# Generated by Django 2.0.2 on 2018-05-11 04:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import recipes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('prepTime', models.CharField(blank=True, max_length=20, null=True)),
                ('servings', models.CharField(blank=True, max_length=50, null=True)),
                ('category', models.CharField(choices=[('', ''), ('Appetizers', 'Appetizers'), ('Soups', 'Soups'), ('Salads', 'Salads'), ('Breads', 'Breads'), ('Main Dishes', 'Main Dishes'), ('Side Dishes', 'Side Dishes'), ('Desserts', 'Desserts'), ('Breakfast and Brunch', 'Breakfast and Brunch'), ('Lunch and Snacks', 'Lunch and Snacks'), ('Beverages', 'Beverages'), ('Cocktails', 'Cocktails'), ('Condiments and Sauces', 'Condiments and Sauces')], max_length=25, null=True)),
                ('instructions', models.TextField(blank=True, null=True)),
                ('yummlyId', models.CharField(blank=True, max_length=100, null=True)),
                ('externalLink', models.URLField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=recipes.models.user_directory_path, validators=[recipes.models.Recipe.validate_image])),
                ('imageUrl', models.URLField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient', models.CharField(max_length=100)),
                ('inventoryItem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryItem')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe')),
            ],
        ),
    ]
