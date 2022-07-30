# Generated by Django 3.2.7 on 2022-07-27 18:09

from django.db import migrations

def apply_migration(apps, schema_editor):    
    Group       = apps.get_model('auth', 'Group')
    Permission  = apps.get_model('auth', 'Permission')

    group = Group.objects.get(name='boat_owner')
    perms = Permission.objects.filter(codename__in=['add_tariff', 'change_tariff', 'view_tariff', 'delete_tariff'])
    group.permissions.add(*perms)

def revert_migration(apps, schema_editor): # pragma: no cover
    Group = apps.get_model('auth', 'Group')
    Permission  = apps.get_model('auth', 'Permission')

    group = Group.objects.get(name='boat_owner')
    perms = Permission.objects.filter(codename__in=['add_tariff', 'change_tariff', 'view_tariff', 'delete_tariff'])
    group.permissions.delete(*perms)

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20220707_2150'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]