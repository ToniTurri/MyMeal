# Generated by Django 2.0.2 on 2018-04-23 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20180423_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='foodItems',
        ),
        migrations.AddField(
            model_name='recipe',
            name='externalLink',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='prepTime',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='servings',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='instructions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
