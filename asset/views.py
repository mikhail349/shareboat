from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Asset

#def get(request):
#    assets = Asset.objects.all()
#    context = {'assets': assets, 'title': 'Все активы'}
#    return render(request, 'asset/list.html', context)

@login_required
def get(request):
    assets = Asset.objects.filter(owner=request.user)
    context = {'assets': assets, 'title': 'Мои активы'}
    return render(request, 'asset/list.html', context)    

@login_required
def create(request):
    if request.method == 'GET':
        return render(request, 'asset/create_update.html')

    elif request.method == 'POST':
        data = request.POST
        asset = Asset.objects.create(name=data['name'], owner=request.user)
        asset.save()
        return redirect('/asset/')

@login_required
@api_view(['POST'])
def delete(request):
    return Response({'data': request.user.email})

