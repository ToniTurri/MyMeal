# Generated by Django 2.0.4 on 2018-04-30 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20180429_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='category',
            field=models.CharField(choices=[('', ''), ('Appetizers', 'Appetizers'), ('Soups', 'Soups'), ('Salads', 'Salads'), ('Breads', 'Breads'), ('Main Dishes', 'Main Dishes'), ('Side Dishes', 'Side Dishes'), ('Desserts', 'Desserts'), ('Breakfast and Brunch', 'Breakfast and Brunch'), ('Lunch and Snacks', 'Lunch and Snacks'), ('Beverages', 'Beverages'), ('Cocktails', 'Cocktails'), ('Condiments and Sauces', 'Condiments and Sauces')], default='', max_length=25),
        ),
    ]
