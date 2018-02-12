# Generated by Django 2.0.1 on 2018-02-09 05:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groceryList', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.IntegerField(default=0)),
            ],
        ),
        migrations.DeleteModel(
            name='GroceryListItems',
        ),
        migrations.AlterField(
            model_name='grocerylist',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='lists',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groceryList.GroceryList'),
        ),
    ]
