from django.shortcuts import render
from .models import Category

def portal(request):
    try:
        category = Category.objects.published().get(full_path=request.path)
    except Category.DoesNotExist:
        category = None

    return render(request, 'portal/portal.html', context={'category': category}) 