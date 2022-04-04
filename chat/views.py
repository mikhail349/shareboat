from re import I
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .models import MessageBooking
from .serializers import MessageBookingSerializerSend, MessageBookingSerializerList
from booking.models import Booking
from django.core.paginator import Paginator

import json
import time

MESSAGES_PER_PAGE = 20

@login_required
def get_new_messages_booking(request, pk):
    if request.method == 'GET':
        last_message_id = request.GET.get('last_message_id', -1)
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))

            while True:
                messages = MessageBooking.objects.filter(booking=booking, recipient=request.user, id__gt=last_message_id).order_by('sent_at')
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
        
        p = Paginator(messages, MESSAGES_PER_PAGE)
        last_page = p.get_page(p.num_pages) 
        messages_serializer = MessageBookingSerializerList(last_page.object_list, many=True, context={'request': request})
        
        context = {
            'messages_page': p.num_pages,
            'booking': booking,
            'messages': json.dumps(messages_serializer.data)
        }
        return render(request, 'chat/booking.html', context=context)
    except Booking.DoesNotExist:
        return render(request, 'not_found.html')    

@login_required
def get_messages_booking(request, pk):
    page_num = request.GET.get('page_num', 1)
    try:
        booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))
        messages = MessageBooking.objects.filter(booking=booking).order_by('sent_at')

        p = Paginator(messages, MESSAGES_PER_PAGE)
        page = p.get_page(page_num) 

        messages_serializer = MessageBookingSerializerList(page.object_list, many=True, context={'request': request})
        return JsonResponse({'data': messages_serializer.data})
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Бронирование не найдено'}, status=400)   
