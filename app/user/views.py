import random
import requests

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, \
                                logout as django_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Group
import jwt

from config import tokens
from config.exceptions import InvalidToken
from emails.models import UserEmail
from user.forms import UpdateForm
from emails.exceptions import EmailLagError
from notification import utils as notify
from .models import User, TelegramUser

import logging
logger_admin_mails = logging.getLogger('mail_admins')
logger = logging.getLogger(__name__)

BOAT_OWNER_GROUP = 'boat_owner'


@permission_required('user.view_support', raise_exception=True)
def support(request):
    return render(request, 'user/support.html',
                  context={'admin_url': settings.ADMIN_URL})


def get_bool(value):
    if value in (True, 'True', 'true', '1', 'on'):
        return True
    return False


def check_recaptcha(request):  # pragma: no cover
    recaptcha = request.POST.get('g-recaptcha-response')
    if recaptcha:
        resp = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={'secret': settings.RECAPTCHA_SERVERSIDE_KEY,
                  'response': recaptcha})
        return resp.json()['success']
    return False


def get_tgcode_message(code):
    return f'Ваш код для авторизации в Телеграм боте: ' \
           f'<strong>{code}</strong>. Отправьте боту команду ' \
           f'<span class="text-primary">/auth</span> и следуйте инструкциям.'


def verify(request, token):
    User = get_user_model()
    try:
        payload = tokens.check_token(token, tokens.VERIFICATION)
        user = User.objects.get(pk=payload.get('user_id'))
        if not user.email_confirmed:
            user.email_confirmed = True
            user.save()
            django_login(request, user)
            notify.send_greetings_to_user(user)
        return render(request, 'user/verified.html')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist,
            InvalidToken, jwt.InvalidSignatureError,
            jwt.exceptions.DecodeError):
        msg = 'Неверная ссылка'
    except jwt.ExpiredSignatureError:
        msg = 'Ссылка устарела'

    return render(request, 'user/invalid_link.html', context={'msg': msg},
                  status=400)


def send_verification_email(request, email):
    try:
        user = User.objects.get(email=email)
        if not user.email_confirmed:
            UserEmail.send_verification_email(request, user)
    except (User.DoesNotExist, EmailLagError):
        pass
    return JsonResponse({})


@login_required
def update_avatar(request):
    avatar = request.FILES.get('avatar')
    user = request.user
    user.avatar = avatar
    user.avatar_sm = avatar
    user.save()

    return JsonResponse({
        'avatar': user.avatar.url,
        'avatar_sm': user.avatar_sm.url
    })


@login_required
def update(request):
    def _get_tgcode_message():
        if (hasattr(request.user, 'telegramuser') and
                not request.user.telegramuser.chat_id):
            return get_tgcode_message(
                request.user.telegramuser.verification_code)
        return ''

    if request.method == 'GET':
        initial = {
            'is_boat_owner': request.user.groups
                                         .filter(name=BOAT_OWNER_GROUP)
                                         .exists()
        }
        form = UpdateForm(instance=request.user, initial=initial)
        return render(request, 'user/update.html',
                      context={'form': form,
                               'tgcode_message': _get_tgcode_message()})

    elif request.method == 'POST':
        user = request.user
        form = UpdateForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return render(request, 'user/update.html',
                          context={'form': form,
                                   'success': 'Профиль сохранен.'})

        return render(request, 'user/update.html',
                      context={'form': form,
                               'tgcode_message': _get_tgcode_message()},
                      status=400)


def login(request):
    if request.method == 'GET':
        return render(
            request, 'user/login.html',
            context={'recaptcha_key': settings.RECAPTCHA_CLIENTSIDE_KEY})

    elif request.method == 'POST':
        data = request.POST

        if not settings.DEBUG:  # pragma: no cover
            if not check_recaptcha(request):
                context = {
                    'recaptcha_key': settings.RECAPTCHA_CLIENTSIDE_KEY,
                    'errors': 'Проверка "Я не робот" не пройдена',
                    'email': data['email']
                }
                return render(request, 'user/login.html', context=context)

        email_lower = data['email'].lower()
        user = authenticate(request, email=email_lower,
                            password=data['password'])
        if user is not None:
            if user.email_confirmed:
                django_login(request, user)
                return redirect(request.POST.get('next') or '/')

            try:
                UserEmail.send_verification_email(request, user)
            except Exception as e:  # pragma: no cover
                logger.error(str(e))

            context = {
                'title': 'Подтвердите почтовый адрес',
                'content': 'Чтобы пользоваться сервисом, вам необходимо \
                           подтвердить свой почтовый адрес.\nПисьмо с \
                           активацией отправлено на почту %s.' % user.email
            }
            return render(request, 'user/email_sent.html',
                          context=context, status=400)

        context = {
            'recaptcha_key': settings.RECAPTCHA_CLIENTSIDE_KEY,
            'errors': 'Неверный логин и/или пароль',
            'email': data['email']
        }
        return render(request, 'user/login.html', context=context, status=400)


@login_required
def logout(request):
    django_logout(request)
    return redirect('/')


def restore_password(request):
    return render(
        request,
        'user/restore_password.html',
        context={'recaptcha_key': settings.RECAPTCHA_CLIENTSIDE_KEY})


@login_required
def generate_telegram_code(request):
    def _gen_code():
        code = str(random.randint(1, 999999))
        code = '0' * 5 + code
        code = code[-6:]
        return code

    code = _gen_code()
    while TelegramUser.objects \
                      .filter(chat_id__isnull=True, verification_code=code) \
                      .exists():
        code = _gen_code()  # pragma: no cover

    TelegramUser.objects.filter(user=request.user).delete()
    TelegramUser.objects.create(user=request.user, verification_code=code)
    return JsonResponse({
        'verification_code': code,
        'message': get_tgcode_message(code)
    })


def change_password(request, token):
    User = get_user_model()
    try:
        payload = tokens.check_token(token, tokens.RESTORE_PASSWORD)
        user = User.objects.get(pk=payload.get('user_id'))
        if request.method == 'GET':
            return render(request, 'user/change_password.html',
                          context={'email': user.email, 'token': token})
        elif request.method == "POST":
            if not user.email_confirmed:
                user.email_confirmed = True
            user.set_password(request.POST['password1'])
            user.save()
            django_login(request, user)
            return redirect('/')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist,
            InvalidToken, jwt.InvalidSignatureError,
            jwt.exceptions.DecodeError):
        msg = 'Неверная ссылка'
    except jwt.ExpiredSignatureError:
        msg = 'Ссылка устарела'

    return render(request, 'user/invalid_link.html',
                  context={'msg': msg}, status=400)


def send_restore_password_email(request):
    if not settings.DEBUG:  # pragma: no cover
        if not check_recaptcha(request):
            return render(
                request, 'user/restore_password.html',
                context={'recaptcha_key': settings.RECAPTCHA_CLIENTSIDE_KEY,
                         'errors': 'Проверка "Я не робот" не пройдена'})

    try:
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        UserEmail.send_restore_password_email(request, user)
    except (User.DoesNotExist, EmailLagError):
        pass

    context = {
        'title': 'Восстановление пароля',
        'content': 'Письмо для сброса пароля отправлено на почту %s' % email
    }

    return render(request, 'user/email_sent.html', context=context)


def register(request):

    def render_error(msg):
        context = {
            'errors': msg,
            'first_name': data.get('first_name'),
            'recaptcha_key': settings.RECAPTCHA_CLIENTSIDE_KEY
        }
        return render(request, 'user/register.html',
                      context=context, status=400)

    if request.method == 'GET':
        return render(
            request, 'user/register.html',
            context={'recaptcha_key': settings.RECAPTCHA_CLIENTSIDE_KEY})

    elif request.method == "POST":
        data = request.POST

        if not settings.DEBUG:  # pragma: no cover
            if not check_recaptcha(request):
                return render_error('Проверка "Я не робот" не пройдена')

        email_lower = data['email'].lower()

        if User.objects.filter(email=email_lower).exists():
            return render_error(
                '%s уже зарегистрирован в системе' % data['email'])

        if data['password1'] != data['password2']:
            return render_error('Пароли не совпадают')

        user = User.objects.create(
            email=email_lower, first_name=data.get('first_name'))
        user.set_password(data['password1'])
        user.save()

        if get_bool(data.get('is_boat_owner')):
            boat_owner_group, _ = Group.objects.get_or_create(
                name=BOAT_OWNER_GROUP)
            user.groups.add(boat_owner_group)

        try:
            UserEmail.send_verification_email(request, user)
            logger_admin_mails.info(
                "Зарегистрировался новый пользователь %s" % data['email'])
        except Exception as e:  # pragma: no cover
            logger.error(str(e))

        context = {
            'user': user,
            'title': 'Регистрация пройдена',
            'header': 'Поздравляем, %s!' % user.first_name,
            'content': 'Регистрация в сервисе ShareBoat успешно пройдена.\n\
                       Чтобы пользоваться сервисом, вам необходимо \
                       подтвердить свой почтовый адрес.\nПисьмо с активацией \
                       отправлено на почту %s' % user.email
        }

        return render(request, 'user/email_sent.html', context=context)
