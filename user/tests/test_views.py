from django.test import TestCase, Client
from django.urls import reverse
from django.test.utils import override_settings

from shareboat import tokens
from user.models import User

from user.tests.test_models import create_user
from user.views import get_bool, get_tgcode_message
from file.tests.test_models import get_imagefile

from time import sleep
import json

class TestCase(TestCase):

    def setUp(self):
        self.client = Client()

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
        response = self.client.get(reverse('user:register'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '456', 'first_name': 'User'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['errors'], 'Пароли не совпадают')

        response = self.client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '123', 'first_name': 'User'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].groups.filter(name='boat_owner').exists())
        self.assertEqual(response.context['title'], 'Регистрация пройдена')

        response = self.client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '123', 'first_name': 'User'})
        self.assertEqual(response.status_code, 400)       
        self.assertEqual(response.context['errors'], 'user@mail.com уже зарегистрирован в системе')

    @override_settings(DEBUG=True) # deactivate recaptcha
    def test_register_boat_owner(self):
        response = self.client.post(reverse('user:register'), {'email': 'user@mail.com', 'password1': '123', 'password2': '123', 'first_name': 'User', 'is_boat_owner': True})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].groups.filter(name='boat_owner').exists())
        self.assertEqual(response.context['title'], 'Регистрация пройдена')

    def test_verify(self):
        user = create_user('user@mail.com', '12345')
        token = tokens.generate_token(user, tokens.VERIFICATION, minutes=0, seconds=1)
    
        sleep(2)
        response = self.client.post(reverse('user:verify', kwargs={'token': token}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['msg'], 'Ссылка устарела')
        
        response = self.client.post(reverse('user:verify', kwargs={'token': 'invalid_token'}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['msg'], 'Неверная ссылка')

        token = tokens.generate_token(user, tokens.VERIFICATION)
        response = self.client.post(reverse('user:verify', kwargs={'token': token}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.get(pk=user.pk).email_confirmed)

    def test_send_verification_email(self):
        user = create_user('user@mail.com', '12345')    
        response = self.client.post(reverse('user:send_verification_email', kwargs={'email': user.email}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('user:send_verification_email', kwargs={'email': 'invalid@email.ru'}))
        self.assertEqual(response.status_code, 200)

    def test_update_avatar(self):
        url = reverse('user:api_update_avatar')

        user = create_user('user@mail.com', '12345')

        # anon
        response = self.client.post(url)
        self.assertRedirects(response, expected_url=reverse('user:login') + '?next=' + url)

        # login
        self.client.login(email='user@mail.com', password='12345')
        
        avatar = get_imagefile(filename="new_avatar.png", size=(500, 500))
        response = self.client.post(url, {'avatar': avatar})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(pk=user.pk)
        self.assertDictEqual(json.loads(response.content), {
            'avatar': user.avatar.url,
            'avatar_sm': user.avatar_sm.url
        })