# Generated by Django 3.2.7 on 2022-08-18 08:41

from django.contrib.auth.management import create_permissions
from django.apps import apps as apps_config
from django.db import migrations

perms_list = ['add_term', 'change_term', 'view_term', 'delete_term']

def apply_migration(apps, schema_editor):    
    create_permissions(apps_config.get_app_config('boat'))

    Group       = apps.get_model('auth', 'Group')
    Permission  = apps.get_model('auth', 'Permission')

    group = Group.objects.get(name='boat_owner')
    perms = Permission.objects.filter(codename__in=perms_list)
    group.permissions.add(*perms)

def revert_migration(apps, schema_editor): # pragma: no cover
    Group = apps.get_model('auth', 'Group')
    Permission  = apps.get_model('auth', 'Permission')

    group = Group.objects.get(name='boat_owner')
    perms = Permission.objects.filter(codename__in=perms_list)
    group.permissions.delete(*perms)

class Migration(migrations.Migration):

    dependencies = [
        ('boat', '0021_auto_20220818_1130'),
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
