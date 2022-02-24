from re import I
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q

from .models import MessageBooking
from .serializers import MessageBookingSerializerSend
from booking.models import Booking

@login_required
def send_message_booking(request):
    if request.method == 'POST':
        ser = MessageBookingSerializerSend(data=request.POST)
        if ser.is_valid():
            try:
                bookings = Booking.objects.filter(Q(pk=ser.validated_data['booking_id']), Q(renter=request.user) | Q(boat__owner=request.user))
                if not bookings:
                    raise Booking.DoesNotExist()
      
                booking = bookings[0]
                recipient = booking.boat.owner if booking.renter == request.user else booking.renter

                MessageBooking.objects.create(text=ser.validated_data['text'], sender=request.user, recipient=recipient, booking=booking)
                return JsonResponse({'data': 'ok'})
            except Booking.DoesNotExist:
                JsonResponse({'message': 'Бронирование не найдено'}, status=400)
     

        return JsonResponse({'message': ser.errors}, status=400)

@login_required
def booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, renter=request.user)

        context = {
            'booking': booking
        }
        return render(request, 'chat/booking.html', context=context)
    except Booking.DoesNotExist:
        return render(request, 'not_found.html')    