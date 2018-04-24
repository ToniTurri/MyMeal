# Generated by Django 2.0.2 on 2018-04-10 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('groceryList', '0010_auto_20180226_1428'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consumed_Stats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count1', models.IntegerField(default=1)),
                ('count2', models.IntegerField(default=0)),
                ('count3', models.IntegerField(default=0)),
                ('count4', models.IntegerField(default=0)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groceryList.FoodItem')),
            ],
        ),
    ]
