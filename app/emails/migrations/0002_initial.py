# Generated by Django 3.2.7 on 2022-07-01 13:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('emails', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='useremail',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emails', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='useremail',
            unique_together={('user', 'type')},
        ),
    ]
