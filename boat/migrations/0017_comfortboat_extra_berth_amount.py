# Generated by Django 3.2.7 on 2022-07-28 14:15

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boat', '0016_auto_20220727_0009'),
    ]

    operations = [
        migrations.AddField(
            model_name='comfortboat',
            name='extra_berth_amount',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99)]),
        ),
    ]
