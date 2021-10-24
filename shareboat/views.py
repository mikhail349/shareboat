from django.shortcuts import render

def index(request):
    return render(request, 'main.html')

def not_found(request):
    return render(request, 'not_found.html')
