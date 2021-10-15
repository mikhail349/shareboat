from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from asset.models import Asset
from .models import AssetFile
from .serializers import AssetFileSerializer

@login_required
def get_assetfiles(request, pk):
    files = AssetFile.objects.filter(asset__pk=pk, asset__owner=request.user)
    serializer = AssetFileSerializer(files, many=True, context={'request': request})
    #assets = Asset.objects.filter(owner=request.user).order_by('id')
    #context = {'assets': assets, 'title': 'Мои активы'}
    return JsonResponse({'data': serializer.data})
