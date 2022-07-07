from django.shortcuts import redirect, render
from django.db import transaction
from django.db.models import Max, Min, Exists, OuterRef, Value
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from rest_framework.decorators import api_view
from rest_framework import status
from django.core.exceptions import ValidationError
from django.core import serializers
from notification import utils as notify

from .exceptions import PriceDateRangeException
from .models import Boat, BoatFav, BoatPricePeriod, Manufacturer, Model, MotorBoat, ComfortBoat, BoatFile, BoatPrice, BoatCoordinates
from .serializers import BoatFileSerializer, ModelSerializer
from .utils import calc_booking as _calc_booking
from base.models import Base
from booking.models import Booking
from chat.models import MessageBoat

import json
import datetime

def response_not_found():
    return JsonResponse({'message': 'Лодка не найдена'}, status=404)

def get_form_context():
    return {
        'boat_types': Boat.get_types(), 
        'motor_boat_types': json.dumps(Boat.get_motor_boat_types()),
        'comfort_boat_types': json.dumps(Boat.get_comfort_boat_types()),
        'price_types': BoatPrice.get_types(),
        'bases': Base.objects.all(),
        'manufacturers': Manufacturer.objects.all()
    }

def get_bool(value):
    if value in (True, 'True', 'true', '1', 'on'):
        return True
    return False

FILES_LIMIT_COUNT = 10

def refresh_boat_price_period(boat):
    BoatPricePeriod.objects.filter(boat=boat).delete()
    price_period = None
    prices = BoatPrice.objects.filter(boat=boat)
    for price in sorted(prices, key=lambda item: item.start_date):

        if price_period is None:
            price_period = BoatPricePeriod.objects.create(boat=boat, start_date=price.start_date, end_date=price.end_date)
            continue
        
        if price.start_date == price_period.end_date + datetime.timedelta(days=1):
            price_period.end_date = price.end_date
            price_period.save()
            continue

        price_period = BoatPricePeriod.objects.create(boat=boat, start_date=price.start_date, end_date=price.end_date)

def handle_boat_prices(boat, prices):
    BoatPrice.objects.filter(boat=boat).delete()
    for price in prices:
        BoatPrice.objects.create(
            price        =price['price'], 
            start_date  = price['start_date'], 
            end_date    = price['end_date'], 
            boat        = boat
        )
    refresh_boat_price_period(boat) 

@login_required
def get_models(request, pk):
    models = Model.objects.filter(manufacturer__pk=pk)
    return JsonResponse({'data': ModelSerializer(models, many=True).data})

@login_required
@permission_required('boat.view_my_boats', raise_exception=True)
def my_boats(request):
    page = request.GET.get('page', 1)

    boats = Boat.active.filter(owner=request.user).order_by('id')
    p = Paginator(boats, settings.PAGINATOR_BOAT_PER_PAGE).get_page(page)

    context = {
        'boats': p.object_list, 
        'Status': Boat.Status,
        'p': p
    }

    return render(request, 'boat/my_boats.html', context=context) 

@login_required
def favs(request):
    page = request.GET.get('page', 1)

    boats = Boat.published.filter(favs__user=request.user).annotate(in_fav=Value(True)).order_by('id')
    p = Paginator(boats, settings.PAGINATOR_BOAT_PER_PAGE).get_page(page)

    context = {
        'boats': p.object_list, 
        'p': p
    }

    return render(request, 'boat/favs.html', context=context) 

@permission_required('boat.view_boats_on_moderation', raise_exception=True)
def boats_on_moderation(request):
    boats = Boat.objects.filter(status=Boat.Status.ON_MODERATION)
    return render(request, 'boat/boats_on_moderation.html', context={'boats': boats}) 

@permission_required('boat.view_boats_on_moderation', raise_exception=True)
def moderate(request, pk):
    if request.method == 'GET':
        try:
            boat = Boat.objects.get(pk=pk, status=Boat.Status.ON_MODERATION)
            context = {
                'boat': boat,
                'reasons': MessageBoat.get_rejection_reasons()
            }
            return render(request, 'boat/moderate.html', context=context)
        except Boat.DoesNotExist:
            return render(request, 'not_found.html', status=404)

@login_required
@permission_required('boat.change_boat', raise_exception=True)
def set_status(request, pk):
    
    ALLOWED_STATUSES = {
        Boat.Status.DECLINED: (Boat.Status.ON_MODERATION,),
        Boat.Status.SAVED: (Boat.Status.ON_MODERATION,),
        Boat.Status.ON_MODERATION: (Boat.Status.SAVED,),
        Boat.Status.PUBLISHED: (Boat.Status.SAVED,)
    }

    try:
        new_status = int(request.POST.get('status'))
        
        boat = Boat.objects.get(pk=pk, owner=request.user)
        if not new_status in ALLOWED_STATUSES.get(boat.status):
            return JsonResponse({'message': 'Некорректный статус'}, status=status.HTTP_400_BAD_REQUEST)

        boat.status = new_status
        boat.save()

        return JsonResponse({})
    except Boat.DoesNotExist:
        return response_not_found()    

@permission_required('boat.moderate_boats', raise_exception=True)
def accept(request, pk):
    try:
        boat = Boat.objects.get(pk=pk, status=Boat.Status.ON_MODERATION)
                
        if boat.modified != parse_datetime(request.POST.get('modified')):
            context = {
                'boat': boat,
                'reasons': MessageBoat.get_rejection_reasons(),
                'errors': 'Лодка была изменена. Выполните проверку еще раз.'
            }
            return render(request, 'boat/moderate.html', context=context) 
        
        boat.status = Boat.Status.PUBLISHED
        boat.save()
        notify.send_boat_published_to_owner(boat)
        return redirect(reverse('boat:boats_on_moderation'))
    except Boat.DoesNotExist:
        return render(request, 'not_found.html', status=404)

@permission_required('boat.moderate_boats', raise_exception=True)
def reject(request, pk):
    if request.method == 'POST':
        try:
            boat = Boat.objects.get(pk=pk, status=Boat.Status.ON_MODERATION)
            reason = int(request.POST.get('reason'))
            comment = request.POST.get('comment')
            modified = parse_datetime(request.POST.get('modified'))
                   
            reasons = MessageBoat.get_rejection_reasons()

            if boat.modified != modified:
                context = {
                    'boat': boat,
                    'reasons': reasons,
                    'errors': 'Лодка была изменена. Возможно, недочёты исправлены.'
                }
                return render(request, 'boat/moderate.html', context=context) 
            
            boat.status = Boat.Status.DECLINED
            boat.save()

            #reason_display = [item[1] for item in reasons if item[0] == reason][0]
            notify.send_boat_declined_to_owner(boat, comment)

            return redirect(reverse('boat:boats_on_moderation'))
        except Boat.DoesNotExist:
            return render(request, 'not_found.html', status=404)

def search_boats(request):
    q_date_from = request.GET.get('dateFrom')
    q_date_to   = request.GET.get('dateTo') 
    q_boat_types=[int(e) for e in request.GET.getlist('boatType')]
    q_sort = request.GET.get('sort', 'sum_asc')
    q_page = request.GET.get('page', 1)
    q_state = request.GET.get('state')

    boats = Boat.objects.none()
    searched = False

    if q_date_from and q_date_to:
        q_date_from = datetime.datetime.strptime(q_date_from, '%Y-%m-%d')
        q_date_to = datetime.datetime.strptime(q_date_to, '%Y-%m-%d')

        if q_date_from <= q_date_to:
            boats = Boat.published.all()
            if q_boat_types:
                boats = boats.filter(type__in=q_boat_types)

            boats = boats.filter(prices_period__start_date__lte=q_date_from, prices_period__end_date__gte=q_date_to)
            boats = boats.exclude(bookings__in=Booking.objects.blocked_in_range(q_date_from, q_date_to))
            boats = boats.annotate_in_fav(user=request.user)

            if q_state:
                boats = boats.filter(coordinates__state=q_state).union(boats.filter(base__state=q_state))

            boats = list(boats) 
            for boat in boats:
                boat.calculated_booking = _calc_booking(boat.pk, q_date_from, q_date_to)

            boats = sorted(boats, key=lambda boat: boat.calculated_booking.get('sum'), reverse=q_sort.split('_')[1]=='desc')
        searched = True

    p = Paginator(boats, settings.PAGINATOR_BOAT_PER_PAGE).get_page(q_page)

    boats_states = set(Boat.published.filter(coordinates__pk__isnull=False).values_list('coordinates__state', flat=True))
    bases_states = set(Boat.published.filter(base__pk__isnull=False).values_list('base__state', flat=True))
    states = sorted(boats_states | bases_states)

    context = {
        'sort_list': [('sum_asc', 'Сначала дешевые'), ('sum_desc', 'Сначала дорогие')],
        'boat_types': Boat.get_types(),
        'boats': p.object_list,
        'searched': searched,
        'p': p,
        'states': states
    }

    return render(request, 'boat/search_boats.html', context)

def boats(request):
    q_page = request.GET.get('page', 1)
    boats = Boat.published.all().annotate_in_fav(user=request.user)
    p = Paginator(boats, settings.PAGINATOR_BOAT_PER_PAGE).get_page(q_page)
    context = {
        'boats': p.object_list,
        'p': p
    }

    return render(request, 'boat/boats.html', context=context)


def switch_fav(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'data': 'redirect', 'url': reverse('user:login')})

    res = None
    try:
        boat = Boat.objects.get(pk=pk)
        BoatFav.objects.get(boat=boat, user=request.user).delete()
        res = 'deleted'
    except BoatFav.DoesNotExist:
        BoatFav.objects.create(boat=boat, user=request.user)
        res = 'added'
    except Boat.DoesNotExist:
        pass
    return JsonResponse({'data': res})
    
def booking(request, pk):
    if request.method == 'GET':
        try:
            boat = Boat.published.get(pk=pk)
            price_dates = boat.prices.aggregate(first=Min('start_date'), last=Max('end_date'))
            prices = boat.prices.values('start_date', 'end_date')
            accepted_bookings = boat.bookings.filter(status__in=Booking.BLOCKED_STATUSES).values('start_date', 'end_date') 

            context = {
                'boat': boat,
                'first_price_date': price_dates.get('first'),
                'last_price_date': price_dates.get('last'),
                'prices_exist': price_dates.get('last') is not None and price_dates.get('last') >= timezone.localdate(),
                'price_ranges': [[e['start_date'], e['end_date']] for e in prices],
                'accepted_bookings_ranges': [[e['start_date'], e['end_date']] for e in accepted_bookings]
            }
            return render(request, 'boat/booking.html', context=context)
        except Boat.DoesNotExist:
            return render(request, 'not_found.html', status=404)

def calc_booking(request, pk):
    start_date  = parse_date(request.GET.get('start_date'))
    end_date    = parse_date(request.GET.get('end_date'))
    try:
        res = _calc_booking(pk, start_date, end_date)
        return JsonResponse(res)
    except Boat.DoesNotExist:
        return response_not_found()
    except PriceDateRangeException as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def view(request, pk):
    try:
        boat = Boat.active.get(pk=pk, owner=request.user)

        context = {
            'boat': boat
        }
        return render(request, 'boat/view.html', context=context)
    except Boat.DoesNotExist:
        return render(request, 'not_found.html', status=404)

@login_required
@permission_required('boat.add_boat', raise_exception=True)
def create(request):
    if request.method == 'GET':
        context = {
            'boat_coordinates': json.dumps({}),
            **get_form_context()
        }
        return render(request, 'boat/create.html', context=context)

    elif request.method == 'POST':
        return create_or_update(request, None)

@login_required
@permission_required('boat.change_boat', raise_exception=True)
def update(request, pk):

    if request.method == 'GET':
        try:
            boat = Boat.active.get(pk=pk, owner=request.user)
            context = {
                'boat': boat, 
                'prices': serializers.serialize('json', boat.prices.all()),
                **get_form_context()
            }
            return render(request, 'boat/update.html', context=context)
        except Boat.DoesNotExist:
            return render(request, 'not_found.html', status=404)
    elif request.method == 'POST':
        return create_or_update(request, pk)

@login_required
@api_view(['POST'])
@permission_required('boat.delete_boat', raise_exception=True)
def delete(request, pk):
    try:
        boat = Boat.active.get(pk=pk, owner=request.user)
    except Boat.DoesNotExist:
        return response_not_found()

    boat.bookings.filter(status=Booking.Status.PENDING).update(status=Booking.Status.DECLINED)
    if boat.bookings.filter(status__in=[Booking.Status.ACCEPTED, Booking.Status.ACTIVE]).exists():
        return JsonResponse({'message': "По этой лодке уже есть подтвержденные или активные бронирования"}, status=status.HTTP_400_BAD_REQUEST)    

    boat.status = Boat.Status.DELETED
    boat.save()
    return JsonResponse({'redirect': reverse('boat:my_boats')})

@login_required
def get_files(request, pk):
    files = BoatFile.objects.filter(boat__pk=pk, boat__owner=request.user)
    serializer = BoatFileSerializer(files, many=True, context={'request': request})
    return JsonResponse({'data': serializer.data})

def create_or_update(request, pk=None):
    data = request.POST
    files = request.FILES.getlist('file')
    prices = json.loads(data.get('prices'))
    is_custom_location = get_bool(data.get('is_custom_location'))
    prepayment_required = get_bool(data.get('prepayment_required'))
    base = Base.objects.get(pk=data.get('base')) if data.get('base') and not is_custom_location else None
    
    try:
        errors = []
        try:
            model = Model.objects.get(pk=data.get('model'))
        except Model.DoesNotExist:
            errors.append(ValidationError('Модель не найдена', code="invalid_model"))

        if len(files) > FILES_LIMIT_COUNT:
            errors.append(ValidationError(f'Можно приложить не более {FILES_LIMIT_COUNT} фотографий', code="files_count_limit"))

        if errors:
            raise ValidationError(errors)

        with transaction.atomic(): 

            if pk is not None:
                boat = Boat.objects.get(pk=pk, owner=request.user)
                
                boat.name       = data.get('name')
                boat.text       = data.get('text')
                boat.issue_year = data.get('issue_year')
                boat.length     = data.get('length')
                boat.width      = data.get('width')
                boat.draft      = data.get('draft')
                boat.capacity   = data.get('capacity')
                boat.type       = data.get('type')
                boat.prepayment_required = prepayment_required
                boat.base       = base
                boat.model      = model
                
                if boat.status == Boat.Status.DECLINED:
                    boat.status = Boat.Status.SAVED
                elif boat.status == Boat.Status.PUBLISHED:
                    boat.status = Boat.Status.ON_MODERATION
                
                boat.save()
            else:
                fields = {
                    'name':         data.get('name'),
                    'text':         data.get('text'),
                    'issue_year':   data.get('issue_year'),
                    'length':       data.get('length'),
                    'width':        data.get('width'),
                    'draft':        data.get('draft'),
                    'capacity':     data.get('capacity'),
                    'type':         data.get('type'),
                    'prepayment_required': prepayment_required,
                    'base':         base,
                    'model':        model
                }

                boat = Boat.objects.create(**fields, owner=request.user)        

                    
            if boat.is_motor_boat():
                try:
                    motor_boat = MotorBoat.objects.get(boat=boat)
                    motor_boat.motor_amount = data.get('motor_amount')
                    motor_boat.motor_power = data.get('motor_power')
                    motor_boat.save()
                except MotorBoat.DoesNotExist:
                    motor_boat_fields = {
                        'motor_amount': data.get('motor_amount'),
                        'motor_power': data.get('motor_power')
                    }
                    MotorBoat.objects.create(**motor_boat_fields, boat=boat)
            else:
                MotorBoat.objects.filter(boat=boat).delete()

            if boat.is_comfort_boat():
                try:
                    comfort_boat = ComfortBoat.objects.get(boat=boat)
                    comfort_boat.berth_amount     = data.get('berth_amount')
                    comfort_boat.cabin_amount     = data.get('cabin_amount')
                    comfort_boat.bathroom_amount  = data.get('bathroom_amount')
                    comfort_boat.save()
                except ComfortBoat.DoesNotExist:
                    comfort_boat_fields = {
                        'berth_amount':     data.get('berth_amount'),
                        'cabin_amount':     data.get('cabin_amount'),
                        'bathroom_amount':  data.get('bathroom_amount')
                    }
                    ComfortBoat.objects.create(**comfort_boat_fields, boat=boat)
            else:
                ComfortBoat.objects.filter(boat=boat).delete()

            if is_custom_location:
                boat_coordinates = json.loads(data.get('boat_coordinates'))
                lat = round(boat_coordinates.get('lat'), 6)
                lon = round(boat_coordinates.get('lon'), 6)
                address = boat_coordinates.get('address')
                state = boat_coordinates.get('state')
                
                try:
                    bc = BoatCoordinates.objects.get(boat=boat)
                    bc.lat = lat
                    bc.lon = lon
                    bc.address = address
                    bc.state = state
                    bc.save()
                except BoatCoordinates.DoesNotExist:
                    BoatCoordinates.objects.create(boat=boat, lat=lat, lon=lon, address=address, state=state) 
            else:
                BoatCoordinates.objects.filter(boat=boat).delete()

            handle_boat_prices(boat, prices)

            BoatFile.objects.filter(boat=boat).exclude(file__in=files).delete()
            for file in files:
                BoatFile.objects.get_or_create(boat=boat, file=file)

            return JsonResponse({
                'data': {'id': boat.id},
                'redirect': reverse('boat:my_boats')
            })

    except Boat.DoesNotExist:
        return response_not_found()
    except ValidationError as e:
        return JsonResponse({'message': list(e)}, status=status.HTTP_400_BAD_REQUEST)
