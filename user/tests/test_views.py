from django.test import TestCase, Client
from django.urls import reverse
from django.test.utils import override_settings

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

    @override_settings(DEBUG=True) # deactivate recaptcha
    def test_register(self):
        client = Client()
        response = client.get(reverse('user:register'))
        self.assertEqual(response.status_code, 200)

        response = client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '456', 'first_name': 'User'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['errors'], 'Пароли не совпадают')

        response = client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '123', 'first_name': 'User'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].groups.filter(name='boat_owner').exists())
        self.assertEqual(response.context['title'], 'Регистрация пройдена')

        response = client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '123', 'first_name': 'User'})
        self.assertEqual(response.status_code, 400)       
        self.assertEqual(response.context['errors'], 'user@mail.com уже зарегистрирован в системе')

    @override_settings(DEBUG=True) # deactivate recaptcha
    def test_register_boat_owner(self):
        client = Client()
        response = client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '123', 'first_name': 'User', 'is_boat_owner': True})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].groups.filter(name='boat_owner').exists())
        self.assertEqual(response.context['title'], 'Регистрация пройдена')
