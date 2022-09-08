from decimal import Decimal
from datetime import timedelta
import json

from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.db import transaction

from boat.utils import calc_booking
from chat.models import MessageBooking
from notification import utils as notify
from .models import Booking, Prepayment, BoatInfo, BoatInfoCoordinates
from .exceptions import BookingDateRangeException, \
                        BookingDuplicatePendingException
from boat.models import Boat, MotorBoat, ComfortBoat, BoatCoordinates


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
        'calculated_data': data.get('calculated_data'),
        'term_content': data.get('term_content', '')
    }

    return context


@login_required
def confirm(request, boat_pk):
    if request.method == 'POST':
        try:
            context = get_confirm_create_context(request.POST, boat_pk)
        except (ValueError, TypeError, json.decoder.JSONDecodeError,
                Boat.DoesNotExist):
            return render(request, 'not_found.html', status=404)

        return render(request, 'booking/confirm.html', context=context)
    else:
        return render(request, 'not_found.html', status=404)


@login_required
def create(request):
    def _create_boat_info(booking):
        boat = booking.boat

        term_content = None
        if boat.term:
            term_content = boat.term.content

        photo = None
        if boat.files.exists():
            photo = boat.files.all().first().file

        spec = {
            'name': boat.name,
            'text': boat.text,
            'issue_year': boat.issue_year,
            'length': boat.length,
            'width': boat.width,
            'draft': boat.draft,
            'capacity': boat.capacity
        }

        try:
            motor = {
                'motor_amount': boat.motor_boat.motor_amount,
                'motor_power': boat.motor_boat.motor_power
            }
            spec['motor'] = motor
        except MotorBoat.DoesNotExist:
            pass

        try:
            comfort = {
                'berth_amount': boat.comfort_boat.berth_amount,
                'extra_berth_amount': boat.comfort_boat.extra_berth_amount,
                'cabin_amount': boat.comfort_boat.cabin_amount,
                'bathroom_amount': boat.comfort_boat.bathroom_amount
            }
            spec['comfort'] = comfort
        except ComfortBoat.DoesNotExist:
            pass

        boat_info = BoatInfo.objects.create(
            booking=booking,
            prepayment_required=boat.prepayment_required,
            term_content=term_content,
            owner=boat.owner,
            model=boat.model,
            type=boat.type,
            base=boat.base,
            photo=photo,
            spec=json.dumps(spec, default=str)
        )

        try:
            BoatInfoCoordinates.objects.create(
                boat_info=boat_info,
                lon=boat.coordinates.lon,
                lat=boat.coordinates.lat,
                address=boat.coordinates.address,
                state=boat.coordinates.state
            )
        except BoatCoordinates.DoesNotExist:
            pass

    if request.method == 'POST':
        def _render_error(msg):
            url = reverse('boat:booking', kwargs={'pk': context['boat'].pk}) \
                + f'?dateFrom={context["start_date"].isoformat()}' \
                  f'&dateTo={context["end_date"].isoformat()}'
            context['errors'] = f'{msg}. <a href="{url}" ' \
                f'class="link-secondary">Вернуться к бронированию.</a>'
            return render(request, 'booking/confirm.html', context=context,
                          status=400)

        try:
            context = get_confirm_create_context(
                request.POST, request.POST.get('boat_pk'))
        except (ValueError, TypeError, json.decoder.JSONDecodeError,
                Boat.DoesNotExist):
            return render(request, 'not_found.html', status=404)

        calculated_data = calc_booking(
            context['boat'].pk, context['start_date'], context['end_date'])
        if calculated_data.get('sum') != context['total_sum']:
            return _render_error('Тарифы на лодку изменились')

        boat_term_content = (context['boat'].term.content
                             if context['boat'].term
                             else '')
        booking_term_content = context['term_content']
        if booking_term_content != boat_term_content:
            return _render_error('Условия аренды изменились')

        try:
            booking = Booking.objects.create(
                boat=context['boat'],
                renter=request.user,
                start_date=context['start_date'],
                end_date=context['end_date'],
                total_sum=context['total_sum'],
                spec=context['spec']
            )
            _create_boat_info(booking)
            notify.send_initial_booking_to_owner(booking)
            return redirect(reverse('booking:view', kwargs={'pk': booking.pk}))

        except (BookingDateRangeException,
                BookingDuplicatePendingException) as e:
            return _render_error(str(e))


@login_required
def my_bookings(request):
    status = request.GET.get('status')
    bookings = Booking.objects.filter(renter=request.user).filter_by_status(
        status).order_by('-start_date')
    return render(request, 'booking/my_bookings.html',
                  context={'bookings': bookings, 'Status': Booking.Status})


@login_required
def requests(request):
    status = request.GET.get('status')
    requests = Booking.objects.filter(
        boat__owner=request.user).filter_by_status(status).order_by('-pk')
    return render(request, 'booking/requests.html',
                  context={'requests': requests, 'Status': Booking.Status})


@permission_required('user.view_all_bookings', raise_exception=True)
def all(request):
    status = request.GET.get('status')
    bookings = Booking.objects.filter_by_status(status).order_by('-pk')
    return render(request, 'booking/all.html',
                  context={'bookings': bookings, 'Status': Booking.Status})


@login_required
@transaction.atomic
def set_request_status(request, pk):

    ALLOWED_STATUSES = {
        Booking.Status.PENDING: (Booking.Status.DECLINED,
                                 Booking.Status.ACCEPTED),
        Booking.Status.PREPAYMENT_REQUIRED: (Booking.Status.DECLINED,
                                             Booking.Status.ACCEPTED),
    }

    try:
        new_status = int(request.POST.get('status'))
        booking = Booking.objects.get(pk=pk, boat__owner=request.user)

        if new_status not in ALLOWED_STATUSES.get(booking.status):
            return JsonResponse({'message': 'Некорректный статус'},
                                status=400)

        if new_status == Booking.Status.DECLINED:
            message = request.POST.get('message')
            if not message:
                return JsonResponse(
                    {'message': 'Необходимо добавить сообщение'},
                    status=400)

            MessageBooking.objects.create(text=message, sender=request.user,
                                          recipient=booking.renter,
                                          booking=booking)

        if new_status == Booking.Status.ACCEPTED:
            if booking.status == Booking.Status.PENDING:
                if booking.boat.prepayment_required:
                    new_status = Booking.Status.PREPAYMENT_REQUIRED
                    prepayment_until = \
                        (timezone.now() + timedelta(
                            days=int(settings.PREPAYMENT_DAYS_LIMIT)
                        )).date()
                    if prepayment_until > booking.start_date:
                        prepayment_until = booking.start_date
                    Prepayment.objects.create(
                        booking=booking, until=prepayment_until)

        booking.status = new_status
        booking.save()
        notify.send_booking_status(booking, booking.renter)

        return JsonResponse({
            'redirect': (reverse('booking:requests')
                         + request.POST.get('search', ''))
            })
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Бронь не найдена'}, status=404)


@login_required
def view(request, pk):
    try:
        if request.user.has_perm('user.view_all_bookings'):
            booking = Booking.objects.get(pk=pk)
        else:
            booking = Booking.objects.get(Q(pk=pk), Q(
                renter=request.user) | Q(boat__owner=request.user))

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

        if new_status not in ALLOWED_STATUSES.get(booking.status):
            return JsonResponse({'message': 'Некорректный статус'}, status=400)

        booking.status = new_status
        booking.save()
        notify.send_booking_status(booking, booking.boat.owner)

        return JsonResponse({
            'redirect': (reverse('booking:my_bookings')
                         + request.POST.get('search', ''))
        })
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Бронь не найдена'}, status=404)
