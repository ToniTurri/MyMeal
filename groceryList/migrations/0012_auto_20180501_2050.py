# Generated by Django 2.0.4 on 2018-05-02 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('groceryList', '0011_auto_20180423_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroceryItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('quantity', models.IntegerField(default=1)),
                ('date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='grocerylist',
            name='fooditems',
        ),
        migrations.DeleteModel(
            name='FoodItem',
        ),
        migrations.AddField(
            model_name='groceryitems',
            name='groceryList',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groceryList.GroceryList'),
        ),
        migrations.AddField(
            model_name='groceryitems',
            name='inventoryItem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.InventoryItem'),
        ),
    ]
