from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Exists, OuterRef, Subquery

from django.urls import reverse
from .models import Message, MessageBoat, MessageBooking
from .serializers import MessageSerializerList

from boat.models import Boat
from booking.models import Booking

import json

@login_required
def list(request):
    user = request.user
    messages = []

    bookings = Booking.objects.filter(
        Q(renter=user) | Q(boat__owner=user), Exists(MessageBooking.objects.filter(booking=OuterRef('pk')))
    )
    for booking in bookings:
        last_message = MessageBooking.objects.filter(booking=booking).last()
        last_message.href = reverse('chat:booking', kwargs={'pk': booking.pk})
        last_message.title = f'<span class="badge bg-secondary">Бронирование</span><div>{booking.boat.name}</div>'
        messages.append(last_message)

    boats = Boat.objects.filter(Q(owner=user), Exists(MessageBoat.objects.filter(boat=OuterRef('pk'))))
    for boat in boats:
        last_message = MessageBoat.objects.filter(boat=boat).last()
        last_message.href = reverse('chat:boat', kwargs={'pk': boat.pk})
        last_message.title = f'<span class="badge bg-secondary">Лодка</span><div>{boat.name}</div>'
        messages.append(last_message)

    system_messages = Message.objects.filter(Q(messageboat__pk__isnull=True), Q(messagebooking__pk__isnull=True), Q(sender=request.user) | Q(recipient=request.user))
    system_message = system_messages.last()
    system_message.href = '#'
    system_message.title = f'<span class="badge bg-secondary">Shareboat</span>'
    messages.append(system_message)

    messages = sorted(messages, key=lambda message: message.pk, reverse=True)
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