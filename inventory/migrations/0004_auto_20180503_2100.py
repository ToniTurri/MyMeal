# Generated by Django 2.0.4 on 2018-05-04 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20180503_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='barcode',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
    ]
