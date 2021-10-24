from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction

from .models import User

@login_required
def update(request):
    if request.method == 'GET':
        return render(request, 'user/update.html')
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                data = request.POST
                user = request.user
                files = request.FILES.getlist('avatar')
                user.first_name = data.get('first_name')

                if user.avatar != files[0]:
                    user.avatar = files[0]

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
        django_login(request, user)
        return redirect('/')
