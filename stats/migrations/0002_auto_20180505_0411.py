# Generated by Django 2.0.2 on 2018-05-05 04:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='time_stamp',
            name='time',
            field=models.DateField(default=datetime.datetime(2018, 5, 5, 4, 11, 16, 275193, tzinfo=utc)),
        ),
    ]