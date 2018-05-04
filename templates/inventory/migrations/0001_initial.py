# Generated by Django 2.0.2 on 2018-05-02 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.IntegerField(default=1)),
                ('barcode', models.CharField(blank=True, max_length=13)),
                ('date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
