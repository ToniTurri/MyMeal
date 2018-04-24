# Generated by Django 2.0.2 on 2018-04-23 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('groceryList', '0011_auto_20180423_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('instructions', models.TextField()),
                ('yummlyRecipeId', models.IntegerField(blank=True, null=True)),
                ('foodItems', models.ManyToManyField(to='groceryList.FoodItem')),
            ],
        ),
    ]
