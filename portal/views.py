from django.shortcuts import render
from .models import Category

def portal(request):
    #BASE_URL = '/portal/'
    
    #path = request.path
    #if path.startswith(BASE_URL):
    #    path = path[len(BASE_URL):]

    try:
        category = Category.m_published.get(full_path=request.path)    
    except Category.DoesNotExist:
        category = None

    return render(request, 'portal/portal.html', context={'category': category}) 