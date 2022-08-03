from django.test import TestCase
from .test_models import get_imagefile, get_file
from user.models import User
from django.core.exceptions import ValidationError

class TestCase(TestCase):
    
    def test_verify_imagefile(self):
        with self.assertRaises(ValidationError) as context:
            avatar = get_imagefile(size=(1920, 1080))
            avatar.size = 10 * 1024**2
            User.objects.create(first_name='User', email='user@mail.com', password="12345", avatar=avatar, avatar_sm=avatar)
        self.assertEqual(context.exception.message, 'Размер файла превышает 7 МБ')

        with self.assertRaises(ValidationError) as context:
            file = get_file()
            User.objects.create(first_name='User', email='user@mail.com', password="12345", avatar=file, avatar_sm=file)
        self.assertEqual(context.exception.message, 'Файл не явялется изображением')

        avatar = get_imagefile(size=(1920, 1080))
        User.objects.create(first_name='User', email='user@mail.com', password="12345", avatar=avatar, avatar_sm=avatar)