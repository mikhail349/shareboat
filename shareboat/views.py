from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.staticfiles.storage import staticfiles_storage

def sw(request):
    file = staticfiles_storage.path('js/sw.js')
    return HttpResponse(open(file).read(), content_type="application/javascript")

def index(request):
    return render(request, 'home.html')

def not_found(request):
    return render(request, 'not_found.html')
