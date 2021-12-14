#from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from notification.models import Notification

@login_required
def delete(request, pk):
    try:
        Notification.objects.get(pk=pk, user=request.user).delete()
        return JsonResponse({})
    except Notification.DoesNotExist:
        return JsonResponse({'message': 'Уведомление не найдено'}, status=404) 

@login_required
def delete_all(request):
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({})
