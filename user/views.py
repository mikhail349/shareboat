from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view

@api_view(['POST', 'GET'])
def login(request):
    
    if request.method == 'GET':
        return render(request, 'user/login.html')   
    
    elif request.method == 'POST':
        data = request.POST
        user = authenticate(request, email=data['email'], password=data['password'])
        if user is not None:
            django_login(request, user)
            #print(request.POST)
            #return redirect('/')
            return redirect(request.POST.get('next'))

        return render(request, 'user/login.html', context={'errors': 'Неверный логин и/или пароль'})


@api_view(['GET'])
def logout(request):
    django_logout(request)
    return redirect('/')
