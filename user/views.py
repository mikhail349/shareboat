from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from shareboat.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text


from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

from .models import User
from .utils import send_verification_email as _send_verification_email

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

    return HttpResponse("Activation link is invalid!")

@login_required
def send_verification_email(request):
    try:
        user = request.user
        if user.email_confirmed:
            return JsonResponse({'message': "Почта %s уже подтверждена" % user.email}, status=400)
        _send_verification_email(request, user)
        return JsonResponse({})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@login_required
def update(request):
    if request.method == 'GET':
        return render(request, 'user/update.html')
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
            print(request.POST.get('next'))
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
            context = {
                'errors': '%s уже зарегистрирован в системе' % data['email']
            }
            return render(request, 'user/register.html', context=context)        

        user = User.objects.create(email=data['email'])
        user.set_password(data['password1'])
        user.save()
        try:
            _send_verification_email(request, user)
        except:
            pass
        django_login(request, user)
        return redirect('/')
