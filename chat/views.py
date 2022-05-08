from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .models import MessageBoat, MessageBooking
from .serializers import MessageBookingSerializerSend, MessageSerializerList

from boat.models import Boat
from booking.models import Booking

import json
import time

@login_required
def get_new_messages_booking(request, pk):
    if request.method == 'GET':
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))

            while True:
                messages = MessageBooking.objects.filter(booking=booking, recipient=request.user, read=False).order_by('sent_at')
                if messages:
                    data = MessageSerializerList(messages, many=True, context={'request': request}).data
                    messages.update(read=True)
                    return JsonResponse({'data': data})
                time.sleep(1)
            
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Бронирование не найдено'}, status=400)

@login_required
def get_new_messages_boat(request, pk):

    def _not_found():
        return JsonResponse({'message': 'Бронирование не найдено'}, status=400)

    if request.method == 'GET':
        try:
            boat = Boat.objects.get(pk=pk)
            is_moderator = request.user.has_perm('boat.can_moderate_boats')

            while True:
                messages = MessageBoat.objects.filter(boat=boat, read=False)
                if boat.owner == request.user:
                    messages = messages.filter(recipient=request.user)
                elif is_moderator:
                    messages = messages.filter(recipient__isnull=True)
                else:
                    return _not_found()      
                messages = messages.order_by('sent_at')

                if messages:
                    data = MessageSerializerList(messages, many=True, context={'request': request}).data
                    messages.update(read=True)
                    return JsonResponse({'data': data})
                time.sleep(1)
            
        except Boat.DoesNotExist:
            return _not_found()

@login_required
def send_message_booking(request, pk):
    if request.method == 'POST':
        data = request.POST
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))
            recipient = booking.boat.owner if booking.renter == request.user else booking.renter
            message = MessageBooking.objects.create(text=data.get('text'), sender=request.user, recipient=recipient, booking=booking)
            message_ser = MessageSerializerList(message, context={'request': request})
            return JsonResponse({'data': message_ser.data})
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

            message = MessageBoat.objects.create(text=data.get('text'), sender=sender, recipient=recipient, boat=boat)
            message_ser = MessageSerializerList(message, context={'request': request})
            return JsonResponse({'data': message_ser.data})
        
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Не удалось отправить сообщение. Лодка не найдена'}, status=400)

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