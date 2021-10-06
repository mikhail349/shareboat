from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Asset

def get(request):
    assets = Asset.objects.all()
    context = {'assets': assets, 'title': 'Все активы'}
    return render(request, 'asset/list.html', context)

@login_required
def get_my(request):
    assets = Asset.objects.filter(owner=request.user)
    context = {'assets': assets, 'title': 'Мои активы'}
    return render(request, 'asset/list.html', context)    

