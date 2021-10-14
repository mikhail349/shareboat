from django.shortcuts import redirect, render
from django.db import transaction
from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
#import json

from .models import Asset
from .serializers import AssetSerializer

@login_required
def get(request):
    assets = Asset.objects.filter(owner=request.user)
    context = {'assets': assets, 'title': 'Мои активы'}
    return render(request, 'asset/list.html', context)    

@login_required
@transaction.atomic
def create(request):
    if request.method == 'GET':
        return render(request, 'asset/create_update.html')

    elif request.method == 'POST':
        data = request.POST
        files = request.FILES.getlist('file')
        print(len(files))
        print(request.FILES)
        #asset = Asset.objects.create(name=data.get('name'), owner=request.user)
        return redirect('/asset/')

@login_required
def update(request, pk):
    try:
        asset = Asset.objects.get(pk=pk, owner=request.user)
        
        if request.method == 'GET':
            return render(request, 'asset/create_update.html', context={'asset': AssetSerializer(asset).data})
        elif request.method == 'POST':
            data = request.POST
            asset.name = data['name']
            asset.save()
            return redirect('/asset/')
    except Asset.DoesNotExist:
        return render(request, 'not_found.html')


@login_required
@api_view(['POST'])
def delete(request, pk):
    try:
        asset = Asset.objects.get(pk=pk, owner=request.user)
    except Asset.DoesNotExist:
        return Response({'message': 'Актив не найден'}, status=status.HTTP_400_BAD_REQUEST)

    if asset.owner != request.user:
        return Response({'message': 'Актив не найден'}, status=status.HTTP_400_BAD_REQUEST)
    
    asset.delete()
    return Response()