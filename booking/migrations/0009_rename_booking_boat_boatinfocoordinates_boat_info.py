# Generated by Django 3.2.7 on 2022-08-25 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0007_auto_20220825_1056'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boatinfocoordinates',
            old_name='booking_boat',
            new_name='boat_info',
        ),
    ]
