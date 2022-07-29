from django.test import TestCase
from user.models import User, TelegramUser
from user.utils import verify_tg_code

class TestCase(TestCase):
    def test_verify_tg_code(self):
        user = User.objects.create(email='ivan@mail.ru', password="12345")
        tg_user = TelegramUser.objects.create(user=user, verification_code='123456')

        self.assertFalse(verify_tg_code(357, '654321'))
        self.assertIsNone(tg_user.chat_id)
 
        self.assertTrue(verify_tg_code(357, '123456'))
        tg_user = TelegramUser.objects.get(user=user)
        self.assertEqual(tg_user.chat_id, 357)     
