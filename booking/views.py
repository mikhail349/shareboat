from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from boat.utils import calc_booking
from chat.models import MessageBooking
from .models import Booking, Prepayment
from .exceptions import BookingDateRangeException, BookingDuplicatePendingException
from boat.models import Boat
from django.db.models import Q
from telegram_bot.notifications import send_message
from django.db import transaction

@login_required
def create(request):
    if request.method == 'POST':
        data = request.POST
        
        start_date  = parse_date(data.get('start_date'))
        end_date    = parse_date(data.get('end_date'))
        total_sum   = float(data.get('total_sum'))
        boat_pk     = data.get('boat_id')

        try:
            boat = Boat.published.get(pk=boat_pk)
        except Boat.DoesNotExist:
            return JsonResponse({'message': 'Лодка не найдена'}, status=404)

        calculated_total_sum = calc_booking(boat_pk, start_date, end_date)
        if calculated_total_sum['sum'] != total_sum:
            return JsonResponse({'message': 'Цена на лодку изменилась', 'code': 'outdated_price'}, status=400)

        try:
            booking = Booking.objects.create(boat=boat, renter=request.user, start_date=start_date, end_date=end_date, total_sum=total_sum)
            MessageBooking.objects.create(booking=booking, sender=None, recipient=boat.owner, text='Новый запрос')
        except (BookingDateRangeException, BookingDuplicatePendingException) as e:
            return JsonResponse({'message': str(e)}, status=400)

        return JsonResponse({'redirect': reverse('booking:view', kwargs={'pk': booking.pk})})

@login_required
def my_bookings(request):
    status = request.GET.get('status')
    bookings = Booking.objects.filter(renter=request.user).filter_by_status(status).order_by('-start_date')
    return render(request, 'booking/my_bookings.html', context={'bookings': bookings, 'Status': Booking.Status})

@login_required
def requests(request):
    status = request.GET.get('status')
    requests = Booking.objects.filter(boat__owner=request.user).filter_by_status(status).order_by('-pk')
    return render(request, 'booking/requests.html', context={'requests': requests, 'Status': Booking.Status})

@login_required
@transaction.atomic
def set_request_status(request, pk):
    
    ALLOWED_STATUSES = {
        Booking.Status.PENDING: (Booking.Status.DECLINED, Booking.Status.ACCEPTED),
    }

    try:
        new_status = int(request.POST.get('status'))
        booking = Booking.objects.get(pk=pk, boat__owner=request.user)

        if not new_status in ALLOWED_STATUSES.get(booking.status):
            return JsonResponse({'message': 'Некорректный статус'}, status=400)

        if new_status == Booking.Status.DECLINED:
            message = request.POST.get('message')
            if not message:
                return JsonResponse({'message': 'Необходимо добавить сообщение'}, status=400)

            MessageBooking.objects.create(text=message, sender=request.user, recipient=booking.renter, booking=booking)

        if new_status == Booking.Status.ACCEPTED:
            if booking.boat.prepayment_required:
                new_status = Booking.Status.PREPAYMENT_REQUIRED
                prepayment_until = timezone.now() + timedelta(days=int(settings.PREPAYMENT_DAYS_LIMIT))
                
                try:
                    booking.prepayment.until = prepayment_until
                    booking.prepayment.save()
                except Prepayment.DoesNotExist:
                    Prepayment.objects.create(booking = booking, until=prepayment_until)

        booking.status = new_status
        booking.save()

        return JsonResponse({'redirect': reverse('booking:requests') + request.POST.get('search', '')})
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Бронь не найдена'}, status=404) 

@login_required
def view(request, pk):
    try:
        booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))

        context = {
            'booking': booking
        }
        return render(request, 'booking/view.html', context=context)
    except Boat.DoesNotExist:
        return render(request, 'not_found.html')

@login_required
def set_status(request, pk):
    
    ALLOWED_STATUSES = {
        Booking.Status.PENDING: (Booking.Status.DECLINED,),
    }

    try:
        new_status = int(request.POST.get('status'))
        booking = Booking.objects.get(pk=pk, renter=request.user)

        if not new_status in ALLOWED_STATUSES.get(booking.status):
            return JsonResponse({'message': 'Некорректный статус'}, status=400)

        booking.status = new_status
        booking.save()

        return JsonResponse({'redirect': reverse('booking:my_bookings') + request.POST.get('search', '')})
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Бронь не найдена'}, status=404)   