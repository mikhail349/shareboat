import imp
from re import M
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Exists, OuterRef, Subquery, F, CharField, Max
from django.db.models.functions import Concat
from django.db.models.expressions import Case, When, Value

from django.urls import reverse
from .models import Message, MessageBoat, MessageBooking, MessageSupport
from .serializers import MessageSerializerList

from boat.models import Boat
from booking.models import Booking
from itertools import chain
from django.utils import timezone

import json

@login_required
def list(request):
    user = request.user
    messages = []
    
    bookings = Booking.objects.filter(Q(renter=user), Exists(MessageBooking.objects.filter(booking=OuterRef('pk'))))
    for booking in bookings:
        last_message = booking.messages.filter(Q(sender=user)).union(booking.messages.filter(Q(recipient=user))).last()
        if last_message:
            last_message.get_badge = lambda: '<div class="badge bg-light text-primary">Бронирование</div>'
            messages.append(last_message)

    requests = Booking.objects.filter(Q(boat__owner=user), Exists(MessageBooking.objects.filter(booking=OuterRef('pk'))))
    for req in requests:
        last_message = req.messages.filter(Q(sender=user)).union(req.messages.filter(Q(recipient=user))).last()
        if last_message:
            last_message.get_badge = lambda: '<div class="badge bg-light text-primary">Заявка на бронирование</div>'
            messages.append(last_message)

    boats = Boat.objects.filter(Q(owner=user), Exists(MessageBoat.objects.filter(boat=OuterRef('pk'))))
    for boat in boats:
        last_message = boat.messages.filter(Q(sender=user)).union(boat.messages.filter(Q(recipient=user))).last()
        if last_message:
            messages.append(last_message)

    last_message_support = MessageSupport.objects.filter(sender=user).union(MessageSupport.objects.filter(recipient=user)).last()
    if last_message_support:
        messages.append(last_message_support)
    
    messages = sorted(messages, key=lambda message: message.pk, reverse=True)

    if not last_message_support:
        last_message_support = MessageSupport(text='Сообщений пока нет', read=True)       
        messages.insert(0, last_message_support)

    return render(request, 'chat/list.html', context={'messages': messages})

@login_required
def get_new_messages_booking(request, pk):
    if request.method == 'GET':
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))

            messages = MessageBooking.objects.filter(booking=booking, recipient=request.user, read=False).order_by('sent_at')
            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.update(read=True)

            return JsonResponse({'data': data})
            
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Бронирование не найдено'}, status=400)

@login_required
def get_new_messages(request):
    if request.method == 'GET':
        messages = MessageSupport.objects.filter(
            recipient=request.user, 
            read=False
        ).order_by('sent_at')
        data = MessageSerializerList(messages, many=True, context={'request': request}).data
        messages.update(read=True)

        return JsonResponse({'data': data})
            

@login_required
def get_new_messages_boat(request, pk):

    def _not_found():
        return JsonResponse({'message': 'Бронирование не найдено'}, status=400)

    if request.method == 'GET':
        try:
            boat = Boat.objects.get(pk=pk)
            is_moderator = request.user.has_perm('boat.can_moderate_boats')

            messages = MessageBoat.objects.filter(boat=boat, read=False)
            if boat.owner == request.user:
                messages = messages.filter(recipient=request.user)
            elif is_moderator:
                messages = messages.filter(recipient__isnull=True)
            else:
                return _not_found()      
            messages = messages.order_by('sent_at')

            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.update(read=True)
            return JsonResponse({'data': data})
            
        except Boat.DoesNotExist:
            return _not_found()

@login_required
def send_message_booking(request, pk):
    if request.method == 'POST':
        data = request.POST
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))
            recipient = booking.boat.owner if booking.renter == request.user else booking.renter
            
            new_message = MessageBooking.objects.create(text=data.get('text'), sender=request.user, recipient=recipient, booking=booking)

            messages = MessageBooking.objects.filter(Q(booking=booking), Q(read=False), Q(recipient=request.user) | Q(pk=new_message.pk)).order_by('sent_at')
            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.filter(recipient=request.user, read=False).update(read=True)

            return JsonResponse({'data': data})
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Не удалось отправить сообщение. Бронирование не найдено'}, status=400)
     

@login_required
def send_message_boat(request, pk):
    if request.method == 'POST':
        data = request.POST
        try:
            boat = Boat.objects.get(pk=pk)
            is_moderator = request.user.has_perm('boat.can_moderate_boats')

            if boat.owner == request.user:
                recipient = None
                sender = boat.owner
            elif is_moderator:
                recipient = boat.owner
                sender = None  
            else:
                return JsonResponse({'message': 'Не удалось отправить сообщение. Лодка не найдена'}, status=400)

            new_message = MessageBoat.objects.create(text=data.get('text'), sender=sender, recipient=recipient, boat=boat)
            
            messages = MessageBoat.objects.filter(Q(boat=boat), Q(read=False), Q(recipient=request.user) | Q(pk=new_message.pk)).order_by('sent_at')
            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.filter(recipient=request.user, read=False).update(read=True)

            return JsonResponse({'data': data})
        
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Не удалось отправить сообщение. Лодка не найдена'}, status=400)

@login_required
def send_message(request):
    if request.method == 'POST':
        data = request.POST
        new_message = MessageSupport.objects.create(text=data.get('text'), sender=request.user, recipient=None)

        messages = MessageSupport.objects.filter(
            Q(read=False), 
            Q(recipient=request.user) | Q(pk=new_message.pk)
        ).order_by('sent_at')
        
        data = MessageSerializerList(messages, many=True, context={'request': request}).data
        messages.filter(recipient=request.user, read=False).update(read=True)

        return JsonResponse({'data': data})
        

@login_required
def message(request):
    messages = MessageSupport.objects.filter(Q(sender=request.user) | Q(recipient=request.user)).order_by('sent_at')
    messages_serializer_data = MessageSerializerList(messages, many=True, context={'request': request}).data

    messages.filter(recipient=request.user, read=False).update(read=True)
    
    context = {
        'messages': json.dumps(messages_serializer_data)
    }
    return render(request, 'chat/message.html', context=context)

@login_required
def booking(request, pk):
    try:
        booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))
        messages = MessageBooking.objects.filter(Q(booking=booking), Q(sender=request.user) | Q(recipient=request.user)).order_by('sent_at')
        messages_serializer_data = MessageSerializerList(messages, many=True, context={'request': request}).data

        messages.filter(recipient=request.user, read=False).update(read=True)
        
        context = {
            'booking': booking,
            'messages': json.dumps(messages_serializer_data)
        }
        return render(request, 'chat/booking.html', context=context)
    except Booking.DoesNotExist:
        return render(request, 'not_found.html') 

@login_required
def boat(request, pk):
    try:
        is_moderator = request.user.has_perm('boat.can_moderate_boats')

        boat = Boat.objects.get(Q(pk=pk))
        if not is_moderator and boat.owner != request.user:
            return render(request, 'not_found.html') 

        messages = MessageBoat.objects.filter(boat=boat)
        if is_moderator:
            messages = messages.filter(Q(sender__isnull=True) | Q(recipient__isnull=True))
        else:
            messages = messages.filter(Q(sender=request.user) | Q(recipient=request.user))
        messages = messages.order_by('sent_at')

        messages_ser_data = MessageSerializerList(messages, many=True, context={'request': request}).data

        if is_moderator:
            messages.filter(recipient__isnull=True, read=False).update(read=True)
        else:
            messages.filter(recipient=request.user, read=False).update(read=True)
        
        context = {
            'boat': boat,
            'messages': json.dumps(messages_ser_data)
        }

        return render(request, 'chat/boat.html', context=context)
    except Boat.DoesNotExist:
        return render(request, 'not_found.html') 