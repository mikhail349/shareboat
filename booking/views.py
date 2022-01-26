from django.shortcuts import render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required

from boat.utils import calc_booking
from .models import Booking
from .exceptions import BookingDateRangeException, BookingDuplicatePendingException
from boat.models import Boat

@login_required
def create(request):
    if request.method == 'POST':
        data = request.POST
        
        start_date  = parse_date(data.get('start_date'))
        end_date    = parse_date(data.get('end_date'))
        total_sum   = float(data.get('total_sum'))
        boat_pk     = data.get('boat_id')

        try:
            boat = Boat.objects.published().get(pk=boat_pk)
        except Boat.DoesNotExist:
            return JsonResponse({'message': 'Лодка не найдена'}, status=404)

        calculated_total_sum = calc_booking(boat_pk, start_date, end_date)
        if calculated_total_sum['sum'] != total_sum:
            return JsonResponse({'message': 'Цена на лодку изменилась', 'code': 'outdated_price'}, status=400)

        try:
            Booking.objects.create(boat=boat, renter=request.user, start_date=start_date, end_date=end_date, total_sum=total_sum)
        except (BookingDateRangeException, BookingDuplicatePendingException) as e:
            return JsonResponse({'message': str(e)}, status=400)

        return JsonResponse({})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(renter=request.user).order_by('id')
    return render(request, 'booking/my_bookings.html', context={'bookings': bookings, 'Status': Booking.Status})