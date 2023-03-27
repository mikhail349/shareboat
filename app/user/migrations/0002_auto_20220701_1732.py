# Generated by Django 3.2.7 on 2022-07-01 14:15
from django.apps import apps as apps_config
from django.contrib.auth.management import create_permissions
from django.db import migrations


def apply_migration(apps, schema_editor):
    create_permissions(apps_config.get_app_config('boat'))
    
    Group       = apps.get_model('auth', 'Group')
    Permission  = apps.get_model('auth', 'Permission')

    group, _ = Group.objects.get_or_create(name='boat_owner')
    perms = Permission.objects.filter(codename__in=['add_boat', 'change_boat', 'view_boat', 'delete_boat'])
    group.permissions.add(*perms)

    group, _ = Group.objects.get_or_create(name='boat_moderator')
    perms = Permission.objects.filter(codename__in=['view_boats_on_moderation', 'moderate_boats'])
    group.permissions.add(*perms)


def revert_migration(apps, schema_editor): # pragma: no cover
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['boat_owner','boat_moderator',]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        ('boat', '0003_alter_boat_options')
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration),
    ]
