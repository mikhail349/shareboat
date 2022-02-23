from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from boat.utils import calc_booking
from .models import Booking
from .exceptions import BookingDateRangeException, BookingDuplicatePendingException
from boat.models import Boat
from django.db.models import Q
from telegram_bot.notifications import send_message

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
            #send_message(boat.owner, f'Добавлена бронь на лодку <a href="{request.build_absolute_uri(reverse("booking:my_bookings"))}">{boat.name}</a>.')
        except (BookingDateRangeException, BookingDuplicatePendingException) as e:
            return JsonResponse({'message': str(e)}, status=400)

        return JsonResponse({'redirect': reverse('booking:view', kwargs={'pk': booking.pk})})

@login_required
def my_bookings(request):
    my_bookings = Booking.objects.filter(renter=request.user)
    
    bookings = my_bookings.filter(~Q(status=Booking.Status.DECLINED)).order_by('-status','-start_date')
    declined_bookings = my_bookings.filter(status=Booking.Status.DECLINED).order_by('-start_date')
    return render(request, 'booking/my_bookings.html', context={'bookings': bookings, 'declined_bookings': declined_bookings, 'Status': Booking.Status})

@login_required
def chat(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, renter=request.user)

        context = {
            'booking': booking
        }
        return render(request, 'booking/chat.html', context=context)
    except Boat.DoesNotExist:
        return render(request, 'not_found.html')    

@login_required
def view(request, pk):
    try:
        booking = Booking.objects.get(pk=pk, renter=request.user)

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

        return JsonResponse({})
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Бронь не найдена'}, status=404)   