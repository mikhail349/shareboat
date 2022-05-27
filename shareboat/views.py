from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

def sw(request):
    return HttpResponse('self.addEventListener("fetch", function(event) {console.log(`start server worker`)});', content_type="application/javascript")

def index(request):
    return render(request, 'home.html')

def not_found(request):
    return render(request, 'not_found.html')
