from django.db.models.fields import EmailField
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from django.contrib.auth import get_user_model

from shareboat.tokens import account_activation_token

import logging
logger_admin_mails = logging.getLogger('mail_admins')
logger = logging.getLogger(__name__)

from .models import User
from emails.models import UserEmail

def verify(request, uidb64, token):
    uid = force_text(urlsafe_base64_decode(uidb64))
    User = get_user_model()
    try: 
        user = User.objects.get(pk=uid)
        if account_activation_token.check_token(user, token):
            if not user.email_confirmed:
                user.email_confirmed = True
                user.save()
            return render(request, 'user/verified.html')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    return render(request, 'user/not_verified.html')

@login_required
def send_verification_email(request):
    try:
        user = request.user
        if user.email_confirmed:
            return JsonResponse({'message': "Почта %s уже подтверждена" % user.email}, status=400)
        dt = UserEmail.send_verification_email(request, user)
        return JsonResponse({'next_verification_email_datetime': dt.isoformat()})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@login_required
def update(request):
    if request.method == 'GET':
        next_verification_email_datetime = UserEmail.get_next_verification_email_datetime(request.user)
        return render(request, 'user/update.html', context={'next_verification_email_datetime': next_verification_email_datetime})
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                data = request.POST
                user = request.user
                avatar = request.FILES.get('avatar')
                user.first_name = data.get('first_name')

                if user.avatar != avatar:
                    user.avatar = avatar

                '''
                email = data.get('email')
                if user.email != email:
                    if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                        raise Exception("Электронная почта %s уже занята" % email)
                    user.email = email
                '''

                user.save()  
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
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

def register(request):

    if request.method == 'GET':
        return render(request, 'user/register.html')

    elif request.method == "POST":
        data = request.POST

        if User.objects.filter(email=data['email']).exists():
            return render(request, 'user/register.html', context={'errors': '%s уже зарегистрирован в системе' % data['email']})        

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
