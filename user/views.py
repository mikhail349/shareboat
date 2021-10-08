from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from user.models import User

def login(request):
    
    if request.method == 'GET':
        return render(request, 'user/login.html')   
    
    elif request.method == 'POST':
        data = request.POST
        user = authenticate(request, email=data['email'], password=data['password'])
        if user is not None:
            django_login(request, user)
            return redirect(request.POST.get('next'))

        return render(request, 'user/login.html', context={'errors': 'Неверный логин и/или пароль'})

def logout(request):
    django_logout(request)
    return redirect('/')

def register(request):

    if request.method == 'GET':
        return render(request, 'user/register.html')

    elif request.method == "POST":
        data = request.POST
        user = User.objects.create(email=data['email'])
        user.set_password(data['password1'])
        user.save()
        django_login(request, user)
        return redirect('/')
