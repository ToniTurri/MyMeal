# Generated by Django 2.0.2 on 2018-04-28 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_auto_20180423_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumed_stats',
            name='total',
            field=models.IntegerField(default=1),
        ),
    ]
