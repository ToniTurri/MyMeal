# Generated by Django 2.0.2 on 2018-02-12 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groceryList', '0003_auto_20180210_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]