from django.test import TestCase, Client
from django.urls import reverse

from user.views import get_bool, get_tgcode_message

class TestCase(TestCase):

    def test_get_bool(self):
        self.assertTrue(get_bool('True'))
        self.assertTrue(get_bool('true'))
        self.assertTrue(get_bool(True))
        self.assertTrue(get_bool(1))
        self.assertTrue(get_bool('1'))
        self.assertTrue(get_bool('on'))

        self.assertFalse(get_bool('False'))
        self.assertFalse(get_bool('false'))
        self.assertFalse(get_bool(False))
        self.assertFalse(get_bool(0))
        self.assertFalse(get_bool('0'))
        self.assertFalse(get_bool('off'))

    def test_get_tgcode_message(self):
        self.assertEqual(
            get_tgcode_message('123456'), 
            'Ваш код для авторизации в Телеграм боте: <strong>123456</strong>. Отправьте боту команду <span class="text-primary">/auth</span> и следуйте инструкциям.'
        )

    def test_register(self):
        client = Client()
        response = client.get(reverse('user:register'))
        self.assertEqual(response.status_code, 200)

        