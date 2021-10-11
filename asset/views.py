from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Asset

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
def delete(request, pk):
    try:
        a = Asset.objects.get(pk=pk)
    except Asset.DoesNotExist:
        return Response({'message': 'Актив не найден'}, status=status.HTTP_400_BAD_REQUEST)

    if a.owner != request.user:
        return Response({'message': 'Актив не найден'}, status=status.HTTP_400_BAD_REQUEST)
    
    a.delete()
    return Response({'data': pk})

