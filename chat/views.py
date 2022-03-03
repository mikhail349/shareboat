from re import I
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .models import MessageBooking
from .serializers import MessageBookingSerializerSend, MessageBookingSerializerList
from booking.models import Booking

import json
import time

@login_required
def get_new_messages_booking(request, pk):
    if request.method == 'GET':
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))

            while True:
                messages = MessageBooking.objects.filter(booking=booking, read=False, recipient=request.user).order_by('sent_at')
                if messages:
                    ser = MessageBookingSerializerList(messages, many=True, context={'request': request})
                    data = ser.data
                    messages.update(read=True)   
                    return JsonResponse({'data': data})
                time.sleep(1)
            
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Бронирование не найдено'}, status=400)

@login_required
def send_message_booking(request):
    if request.method == 'POST':
        ser = MessageBookingSerializerSend(data=request.POST)
        if ser.is_valid():
            try:
                booking = Booking.objects.get(Q(pk=ser.validated_data['booking_id']), Q(renter=request.user) | Q(boat__owner=request.user))
                recipient = booking.boat.owner if booking.renter == request.user else booking.renter
                message = MessageBooking.objects.create(text=ser.validated_data['text'], sender=request.user, recipient=recipient, booking=booking)
                message_ser = MessageBookingSerializerList(message, context={'request': request})
                return JsonResponse({'data': message_ser.data})
            except Booking.DoesNotExist:
                return JsonResponse({'message': 'Не удалось отправить сообщение. Бронирование не найдено'}, status=400)
     

        return JsonResponse({'message': ser.errors}, status=400)

@login_required
def booking(request, pk):
    try:
        booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))
        messages = MessageBooking.objects.filter(booking=booking).order_by('sent_at')
        messages.filter(read=False, recipient=request.user).update(read=True)
        messages_serializer = MessageBookingSerializerList(messages, many=True, context={'request': request})
        context = {
            'booking': booking,
            'messages': json.dumps(messages_serializer.data)
        }
        return render(request, 'chat/booking.html', context=context)
    except Booking.DoesNotExist:
        return render(request, 'not_found.html')    