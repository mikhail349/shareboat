# Generated by Django 3.2.7 on 2022-08-18 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_booking_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='content',
            new_name='term_content',
        ),
    ]