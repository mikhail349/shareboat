from django.shortcuts import render


def index(request):
    return render(request, 'home.html')

def not_found(request):
    return render(request, 'not_found.html')
