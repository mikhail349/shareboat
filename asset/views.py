from django.shortcuts import redirect, render
from django.db import transaction
from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse

from .models import Asset
from .serializers import AssetSerializer
from file.models import AssetFile


def return_not_found():
    return JsonResponse({'message': 'Актив не найден'}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def get(request):
    assets = Asset.objects.filter(owner=request.user).order_by('id')
    return render(request, 'asset/list.html', context={'assets': assets})    

@login_required
@transaction.atomic
def create(request):
    if request.method == 'GET':
        return render(request, 'asset/create_update.html')

    elif request.method == 'POST':
        data = request.POST
        files = request.FILES.getlist('file')
        asset = Asset.objects.create(name=data.get('name'), owner=request.user)
        for file in files:
            AssetFile.objects.create(asset=asset, file=file)

        return JsonResponse({
            'data': {'id': asset.id},
            'redirect': '/asset/'
        })


@login_required
@transaction.atomic
def update(request, pk):
    try:
        asset = Asset.objects.get(pk=pk, owner=request.user)
        
        if request.method == 'GET':
            return render(request, 'asset/create_update.html', context={'asset': AssetSerializer(asset).data})
        elif request.method == 'POST':
            data = request.POST
            files = request.FILES.getlist('file')

            asset.name = data['name']
            asset.save()

            AssetFile.objects.filter(asset=asset).exclude(file__in=files).delete()

            for file in files:
                AssetFile.objects.get_or_create(asset=asset, file=file)

            return JsonResponse({'redirect': '/asset/'})
    
    except Asset.DoesNotExist:
        if request.method == 'GET':
            return render(request, 'not_found.html')
        elif request.method == 'POST':
            return return_not_found()


@login_required
@api_view(['POST'])
def delete(request, pk):
    try:
        asset = Asset.objects.get(pk=pk, owner=request.user)
    except Asset.DoesNotExist:
        return return_not_found()

    if asset.owner != request.user:
        return return_not_found()
    
    asset.delete()
    return Response()