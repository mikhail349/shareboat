from django.test import TestCase
from user.models import User, TelegramUser
from django.contrib.auth.models import Group, Permission
from file.tests.test_models import get_large_imagefile

import json
from types import SimpleNamespace

def create_user(email, password):
    user = User.objects.create(email=email)
    user.set_password(password)
    user.save()
    return user

def create_boat_owner(email, password):
    user = create_user(email, password)

    boat_owner_group, _ = Group.objects.get_or_create(name='boat_owner')     
    perms = Permission.objects.filter(codename__in=['add_boat', 'change_boat', 'view_boat', 'delete_boat'])
    for p in perms:
        boat_owner_group.permissions.add(p)

    user.groups.add(boat_owner_group)  
    return user

def create_moderator(email, password):
    user = create_user(email, password)
    user.groups.add(Group.objects.get(name='boat_moderator'))
    return user

class TelegramBotUpdateFake:
    pass

class UserTestCase(TestCase):
    def test_create(self):
        avatar = get_large_imagefile()
        user = User.objects.create(first_name='Иван', email='ivan@mail.ru', password="12345", avatar=avatar, avatar_sm=avatar)
        self.assertLessEqual(user.avatar_sm.width, 64)
        self.assertLessEqual(user.avatar_sm.height, 64)
        self.assertIsNone(user.get_telegram_id())

        update = {
            'message': {
                'from_user': {
                    'id': 357
                }
            }
        }
        update = json.loads(
            json.dumps(update), object_hook=lambda d: SimpleNamespace(**d)
        )   
        self.assertIsNone(TelegramUser.get_user(update))

        tg_user = TelegramUser.objects.create(user=user, verification_code='123456', chat_id=357)
        self.assertTrue(tg_user, TelegramUser.get_user(update))
        self.assertTrue(user.get_telegram_id(), 357)
        

    def test_cmd_create(self):
        User.objects.create_user(first_name='Иван', email='ivan@mail.ru', password="12345")

        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email=None, password="12345")
        self.assertTrue(context.exception, 'The given email must be set')

        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(email='ivan@mail.ru', password="12345", is_staff=False)
        self.assertTrue(context.exception, 'Superuser must have is_staff=True.')       

        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(email='ivan@mail.ru', password="12345", is_superuser=False)
        self.assertTrue(context.exception, 'Superuser must have is_superuser=True.')    

        User.objects.create_superuser(email='admin@mail.ru', password="12345")