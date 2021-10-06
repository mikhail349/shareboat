from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login

from rest_framework.decorators import api_view
from django.http import HttpResponse

def login(request):
    return render(request, 'user/login.html')

@api_view(['POST'])
def auth(request):
    data = request.POST
    user = authenticate(request, email=data['email'], password=data['password'])
    if user is not None:
        django_login(request, user)
        return HttpResponse('Auth ok')
    else:
        return HttpResponse('Invalid login')
