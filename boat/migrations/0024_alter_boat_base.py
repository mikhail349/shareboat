# Generated by Django 3.2.7 on 2022-08-18 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('boat', '0023_alter_boat_term'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boat',
            name='base',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='boats', to='base.base'),
        ),
    ]
