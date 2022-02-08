from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth import get_user_model
from emails.exceptions import EmailLagError
import jwt

from shareboat import tokens
from shareboat.exceptions import InvalidToken
from emails.models import UserEmail
from .models import User

import logging
logger_admin_mails = logging.getLogger('mail_admins')
logger = logging.getLogger(__name__)


def verify(request, token):
    User = get_user_model()
    try: 
        payload = tokens.check_token(token, tokens.VERIFICATION)
        user = User.objects.get(pk=payload.get('user_id'))
        if not user.email_confirmed:
            user.email_confirmed = True
            user.save()
        return render(request, 'user/verified.html')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, InvalidToken, jwt.InvalidSignatureError):
        msg = 'Неверная ссылка'
    except jwt.ExpiredSignatureError:
        msg = 'Ссылка устарела'

    return render(request, 'user/invalid_link.html', context={'msg': msg})

@login_required
def send_verification_email(request):
    try:
        user = request.user
        if user.email_confirmed:
            return JsonResponse({'message': "Почта %s уже подтверждена" % user.email}, status=400)
        dt = UserEmail.send_verification_email(request, user)
        return JsonResponse({'next_verification_email_datetime': dt.isoformat()})
    except EmailLagError as e:
        return JsonResponse({'message': str(e)}, status=400)

@login_required
def update(request):
    if request.method == 'GET':
        next_verification_email_datetime = UserEmail.get_next_email_datetime(request.user, type=UserEmail.Type.VERIFICATION)
        return render(request, 'user/update.html', context={'next_verification_email_datetime': next_verification_email_datetime})
    elif request.method == 'POST':
        with transaction.atomic():
            data = request.POST
            user = request.user
            avatar = request.FILES.get('avatar')
            user.first_name = data.get('first_name')

            if user.avatar != avatar:
                user.avatar = avatar

            user.save()  
        return JsonResponse({})


def login(request):
    if request.method == 'GET':
        return render(request, 'user/login.html')   
    
    elif request.method == 'POST':
        data = request.POST
        user = authenticate(request, email=data['email'], password=data['password'])
        if user is not None:
            django_login(request, user)
            return redirect(request.POST.get('next'))

        context = {
            'errors': 'Неверный логин и/или пароль',
            'email': data['email']
        }
        return render(request, 'user/login.html', context=context)

@login_required
def logout(request):
    django_logout(request)
    return redirect('/')

def restore_password(request):
    return render(request, 'user/restore_password.html')

def change_password(request, token):
    User = get_user_model() 
    try:
        payload = tokens.check_token(token, tokens.RESTORE_PASSWORD)
        user = User.objects.get(pk=payload.get('user_id'))
        if request.method == 'GET':
            return render(request, 'user/change_password.html', context={'email': user.email, 'token': token})
        elif request.method == "POST":
            user.set_password(request.POST['password1'])
            user.save()
            django_login(request, user)
            return redirect('/')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, InvalidToken, jwt.InvalidSignatureError):
        msg = 'Неверная ссылка'
    except jwt.ExpiredSignatureError:
        msg = 'Ссылка устарела'

    return render(request, 'user/invalid_link.html', context={'msg': msg})
    

def send_restore_password_email(request):
    try:
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        dt = UserEmail.send_restore_password_email(request, user)
        return JsonResponse({'next_email_datetime': dt.isoformat()})
    
    except User.DoesNotExist:
        return JsonResponse({'message': 'Почтовый адрес %s не найден в системе' % email}, status=400)
    except EmailLagError as e:
        return JsonResponse({'message': str(e)}, status=400)

def register(request):

    def render_error(msg):
        return render(request, 'user/register.html', context={'errors': msg, 'first_name': data.get('first_name')})  

    if request.method == 'GET':
        return render(request, 'user/register.html')

    elif request.method == "POST":
        data = request.POST

        if User.objects.filter(email=data['email']).exists():
            return render_error('%s уже зарегистрирован в системе' % data['email'])      

        if data['password1'] != data['password2']:
            return render_error('Пароли не совпадают')  

        user = User.objects.create(email=data['email'], first_name=data.get('first_name'))
        user.set_password(data['password1'])
        user.save()
        django_login(request, user)
        
        try:
            UserEmail.send_verification_email(request, user)
            logger_admin_mails.info("Зарегистрировался новый пользователь %s" % data['email'])
        except Exception as e:
            logger.error(str(e))
        
        return redirect('/')
