import json
from time import sleep

from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from boat.models import Boat
from boat.tests.test_models import create_model, create_simple_boat
from config import tokens
from file.tests.test_models import get_imagefile
from user.models import TelegramUser, User
from user.tests.test_models import create_boat_owner, create_user
from user.views import get_bool, get_tgcode_message


class UserTestCase(TestCase):

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

    def test_update(self):
        url = reverse('user:update')

        owner = create_boat_owner('user@mail.com', '12345')

        # anon
        response = self.client.get(url)
        self.assertRedirects(response, expected_url=reverse('user:login') + '?next=' + url)

        # login
        self.client.login(email='user@mail.com', password='12345')         
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial['is_boat_owner'], True)
        self.assertEqual(response.context['form'].instance.email, 'user@mail.com')
        self.assertEqual(response.context['tgcode_message'], '')
        
        TelegramUser.objects.create(user=owner, verification_code='333')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['tgcode_message'], 'Ваш код для авторизации в Телеграм боте: <strong>333</strong>. Отправьте боту команду <span class="text-primary">/auth</span> и следуйте инструкциям.')


        boat = create_simple_boat(create_model(), owner)
        response = self.client.post(url, {'is_boat_owner': False, 'first_name': 'The Owner'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(list(response.context['form'].errors.items())[0][1][0], '- Для того чтобы перестать быть арендодателем, необходимо удалить свой флот')

        response = self.client.post(url, {'is_boat_owner': True, 'first_name': 'The Owner'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance.first_name, 'The Owner')

        Boat.objects.all().delete()
        response = self.client.post(url, {'is_boat_owner': False, 'first_name': 'The Owner'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].instance.groups.all().exists())

    @override_settings(RECAPTCHA_CLIENTSIDE_KEY='rck123', DEBUG=True) # deactivate recaptcha
    def test_login(self):
        url = reverse('user:login')

        user = create_user('user@mail.com', '12345')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recaptcha_key'], 'rck123')

        response = self.client.post(url, {'email': 'wrong@mail.com', 'password': '12345'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['recaptcha_key'], 'rck123')
        self.assertEqual(response.context['email'], 'wrong@mail.com')
        self.assertEqual(response.context['errors'], 'Неверный логин и/или пароль')

        response = self.client.post(url, {'email': 'user@mail.com', 'password': '12345'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['title'], 'Подтвердите почтовый адрес')

        user.email_confirmed = True
        user.save()
        response = self.client.post(url, {'email': 'user@mail.com', 'password': '12345'})
        self.assertRedirects(response, expected_url='/')

    def test_logout(self):
        create_user('user@mail.com', '12345')
        self.client.login(email='user@mail.com', password='12345')
        response = self.client.post(reverse('user:logout'))
        self.assertRedirects(response, expected_url='/')

    @override_settings(RECAPTCHA_CLIENTSIDE_KEY='rck123')
    def test_restore_password(self):
        response = self.client.get(reverse('user:restore_password'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recaptcha_key'], 'rck123')

    def test_generate_telegram_code(self):
        url = reverse('user:generate_telegram_code')

        user = create_user('user@mail.com', '12345')

        # anon
        response = self.client.get(url)
        self.assertRedirects(response, expected_url=reverse('user:login') + '?next=' + url)

        # login
        self.client.login(email='user@mail.com', password='12345')      
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        tg_code = TelegramUser.objects.get(user=user).verification_code
        content = json.loads(response.content)
        self.assertEqual(content['verification_code'], tg_code)
        self.assertEqual(content['message'], 'Ваш код для авторизации в Телеграм боте: <strong>%s</strong>. Отправьте боту команду <span class="text-primary">/auth</span> и следуйте инструкциям.' % tg_code)

    def test_change_password(self):
        user = create_user('user@mail.com', '12345')
        token = tokens.generate_token(user, tokens.RESTORE_PASSWORD, minutes=0, seconds=1)
    
        sleep(2)
        response = self.client.get(reverse('user:change_password', kwargs={'token': token}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['msg'], 'Ссылка устарела')
        
        response = self.client.get(reverse('user:change_password', kwargs={'token': 'invalid_token'}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context['msg'], 'Неверная ссылка')

        token = tokens.generate_token(user, tokens.RESTORE_PASSWORD)
        response = self.client.get(reverse('user:change_password', kwargs={'token': token}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['email'], 'user@mail.com')
        self.assertEqual(response.context['token'], token)

        response = self.client.post(reverse('user:change_password', kwargs={'token': token}), {'password1': 'new_password'})
        self.assertRedirects(response, expected_url='/')
        self.assertTrue(User.objects.get(pk=user.pk).email_confirmed)        

    @override_settings(DEBUG=True) # deactivate recaptcha
    def test_send_restore_password_email(self):
        user = create_user('user@mail.com', '12345')
        
        # wrong email 
        response = self.client.post(reverse('user:send_restore_password_email'), {'email': 'wrong@mail.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Восстановление пароля')

        # ok
        response = self.client.post(reverse('user:send_restore_password_email'), {'email': 'user@mail.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['title'], 'Восстановление пароля')