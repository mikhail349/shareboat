from decimal import Decimal
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from boat.utils import calc_booking
from chat.models import MessageBooking
from notification import utils as notify 

from .models import Booking, Prepayment
from .exceptions import BookingDateRangeException, BookingDuplicatePendingException
from .templatetags.booking_extras import spectolist

from boat.models import Boat
from django.db.models import Q
from telegram_bot.notifications import send_message
from django.db import transaction

import json

def get_confirm_create_context(data, boat_pk):
    boat = Boat.published.get(pk=boat_pk)
    start_date = parse_date(data.get('start_date'))
    end_date = parse_date(data.get('end_date'))
    calculated_data = json.loads(data.get('calculated_data'))
    
    context = {
        'boat': boat,
        'start_date': start_date,
        'end_date': end_date,
        'days': int(calculated_data.get('days')),
        'total_sum': Decimal(calculated_data.get('sum')),
        'spec': json.dumps(calculated_data.get('spec'), default=str),
        'calculated_data': data.get('calculated_data')
    }

    return context

@login_required
def confirm(request, boat_pk):
    if request.method == 'POST': 
        try:
            context = get_confirm_create_context(request.POST, boat_pk)
        except (ValueError, TypeError, json.decoder.JSONDecodeError, Boat.DoesNotExist):
            return render(request, 'not_found.html', status=404)

        return render(request, 'booking/confirm.html', context=context)
    else:
        return render(request, 'not_found.html', status=404)

@login_required
def create(request):
    if request.method == 'POST':
        def _render_error(msg):
            url = reverse('boat:booking', kwargs={'pk': context['boat'].pk}) + f'?dateFrom={context["start_date"].isoformat()}&dateTo={context["end_date"].isoformat()}'
            context['errors'] = f'{msg}. <a href="{url}" class="link-secondary">Вернуться к бронированию.</a>'
            return render(request, 'booking/confirm.html', context=context, status=400)

        try:
            context = get_confirm_create_context(request.POST, request.POST.get('boat_pk'))
        except (ValueError, TypeError, json.decoder.JSONDecodeError, Boat.DoesNotExist):
            return render(request, 'not_found.html', status=404)

        calculated_data = calc_booking(context['boat'].pk, context['start_date'], context['end_date'])
        if calculated_data.get('sum') != context['total_sum']:
            return _render_error('Тарифы на лодку изменились')

        try:
            booking = Booking.objects.create(
                boat=context['boat'], 
                renter=request.user, 
                start_date=context['start_date'], 
                end_date=context['end_date'], 
                total_sum=context['total_sum'], 
                spec=context['spec']
            )
            notify.send_initial_booking_to_owner(booking)
            return redirect(reverse('booking:view', kwargs={'pk': booking.pk}))

        except (BookingDateRangeException, BookingDuplicatePendingException) as e:
            return _render_error(str(e))

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
                Prepayment.objects.create(booking=booking, until=prepayment_until)

        booking.status = new_status
        booking.save()
        notify.send_booking_status(booking, booking.renter)

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
    except Booking.DoesNotExist:
        return render(request, 'not_found.html', status=404)

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
        notify.send_booking_status(booking, booking.boat.owner)

        return JsonResponse({'redirect': reverse('booking:my_bookings') + request.POST.get('search', '')})
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Бронь не найдена'}, status=404)   