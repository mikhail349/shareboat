# Generated by Django 3.2.7 on 2022-07-26 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boat', '0011_remove_tariff_max'),
    ]

    operations = [
        migrations.AddField(
            model_name='tariff',
            name='duration_display',
            field=models.CharField(default=1, help_text='Рассчитывается автоматически', max_length=255, verbose_name='Текстовое представление продлжительности'),
            preserve_default=False,
        ),
    ]
