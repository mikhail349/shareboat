# Generated by Django 3.2.7 on 2022-07-01 13:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portal', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles', to=settings.AUTH_USER_MODEL, verbose_name='Создатель'),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('url', 'parent')},
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together={('url', 'category')},
        ),
    ]
