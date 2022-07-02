from django.test import TestCase
from user.models import User
from django.contrib.auth.models import Group, Permission

def create_boat_owner(email, password):
    user = User.objects.create(email=email)
    user.set_password(password)
    user.save()

    boat_owner_group, _ = Group.objects.get_or_create(name='boat_owner')     
    perms = Permission.objects.filter(codename__in=['add_boat', 'change_boat', 'view_boat', 'delete_boat'])
    for p in perms:
        boat_owner_group.permissions.add(p)

    user.groups.add(boat_owner_group)  
    return user