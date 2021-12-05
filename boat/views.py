
from decimal import Decimal
from django.shortcuts import redirect, render
from django.db import transaction
from django.db.models import Max, Min
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from rest_framework.decorators import api_view
from rest_framework import status
from PIL import UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core import serializers

from shareboat.date_utils import daterange

from file.exceptions import FileSizeException
from .exceptions import BoatFileCountException, PriceDateRangeException
from .models import Boat, BoatDeclinedModeration, MotorBoat, ComfortBoat, BoatFile, BoatPrice
from .serializers import BoatFileSerializer
from .utils import calc_booking as _calc_booking, my_boats as _my_boats

import json


def response_not_found():
    return JsonResponse({'message': 'Лодка не найдена'}, status=404)

def response_invalid_file_type():
    return JsonResponse({'message': 'Можно приложить только фотографии'}, status=status.HTTP_400_BAD_REQUEST)

def response_files_limit_count(msg):
    return JsonResponse({'message': msg}, status=status.HTTP_400_BAD_REQUEST)

def response_file_limit_size(msg):
    return JsonResponse({'message': msg}, status=status.HTTP_400_BAD_REQUEST)

def get_form_context():
    return {
        'boat_types': Boat.get_types(), 
        'motor_boat_types': json.dumps(Boat.get_motor_boat_types()),
        'comfort_boat_types': json.dumps(Boat.get_comfort_boat_types()),
        'price_types': BoatPrice.get_types(),
        #'categories': Specification.get_сategories()
    }

def get_bool(value):
    if value in (True, 'True', 'true', '1', 'on'):
        return True
    return False

FILES_LIMIT_COUNT = 10

def handle_boat_prices(boat, prices):
    BoatPrice.objects.filter(boat=boat).exclude(id__in=[price.get('pk') for price in prices]).delete()
    for price in prices:
        if 'pk' in price:
            try:
                boat_price = BoatPrice.objects.get(pk=price['pk'])
                boat_price.price        = price['price']
                boat_price.type         = price['type']
                boat_price.start_date   = price['start_date']
                boat_price.end_date     = price['end_date']
                boat_price.boat         = boat
                boat_price.save()
            except BoatPrice.DoesNotExist:
                pass
        else:
            BoatPrice.objects.create(
                price        =price['price'], 
                type        = price['type'], 
                start_date  = price['start_date'], 
                end_date    = price['end_date'], 
                boat        = boat
            )

@login_required
def my_boats(request):
    boats = Boat.objects.filter(owner=request.user).order_by('id')
    return render(request, 'boat/my_boats.html', context={'boats': boats, 'Status': Boat.Status}) 

@permission_required('boat.can_view_boats_on_moderation', raise_exception=True)
def boats_on_moderation(request):
    boats = Boat.objects.filter(status=Boat.Status.ON_MODERATION)
    return render(request, 'boat/boats_on_moderation.html', context={'boats': boats}) 

@permission_required('boat.can_view_boats_on_moderation', raise_exception=True)
def moderate(request, pk):
    if request.method == 'GET':
        try:
            boat = Boat.objects.get(pk=pk, status=Boat.Status.ON_MODERATION)
            context = {
                'boat': boat,
                'reasons': BoatDeclinedModeration.get_reasons()
            }
            return render(request, 'boat/moderate.html', context=context)
        except Boat.DoesNotExist:
            return render(request, 'not_found.html')

@login_required
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

        BoatDeclinedModeration.objects.filter(boat=boat).delete()

        return JsonResponse({})
    except Boat.DoesNotExist:
        return response_not_found()    

@permission_required('boat.can_moderate_boats', raise_exception=True)
def accept_boat(request, pk):
    if request.method == 'POST':
        try:
            boat = Boat.objects.get(pk=pk, status=Boat.Status.ON_MODERATION)
                   
            if boat.modified != parse_datetime(request.POST.get('modified')):
                return JsonResponse({'code': 'outdated', 'message': 'Данные лодки были изменены'}, status=status.HTTP_400_BAD_REQUEST)
            
            boat.status = Boat.Status.PUBLISHED
            boat.save()
            return JsonResponse({'redirect': reverse('boat:boats_on_moderation')})
        except Boat.DoesNotExist:
            return response_not_found()

@permission_required('boat.can_moderate_boats', raise_exception=True)
def decline_boat(request, pk):
    if request.method == 'POST':
        try:
            boat = Boat.objects.get(pk=pk, status=Boat.Status.ON_MODERATION)
            reason = request.POST.get('reason')
            comment = request.POST.get('comment')
            modified = parse_datetime(request.POST.get('modified'))
                   
            if boat.modified != modified:
                return JsonResponse({'code': 'outdated', 'message': 'Данные лодки были изменены'}, status=status.HTTP_400_BAD_REQUEST)
            
            boat.status = Boat.Status.DECLINED
            boat.save()

            try:
                boat_declined_moderation = BoatDeclinedModeration.objects.get(boat=boat)
                boat_declined_moderation.reason=reason
                boat_declined_moderation.comment=comment
                boat_declined_moderation.save()
            except BoatDeclinedModeration.DoesNotExist:
                BoatDeclinedModeration.objects.create(boat=boat, reason=reason, comment=comment)

            return JsonResponse({'redirect': reverse('boat:boats_on_moderation')})
        except Boat.DoesNotExist:
            return response_not_found()


def boats(request):
    q_boat_types=[int(e) for e in request.GET.getlist('boatType')]
    q_price_type=request.GET.get('priceType')
    q_price_from=request.GET.get('priceFrom')
    q_price_to  =request.GET.get('priceTo')
    q_date_from =request.GET.get('dateFrom')
    q_date_to   =request.GET.get('dateTo') 
    q_page      =request.GET.get('page', 1)

    #boat_prices = BoatPrice.objects.all()
    #if q_price_type:
    #    boat_prices = boat_prices.filter(type=q_price_type) 
    #if q_price_from:
    #    boat_prices = boat_prices.filter(price__gte=q_price_from)
    #if q_price_to:
    #    boat_prices = boat_prices.filter(price__lte=q_price_to)
    #if q_date_from:
    #    boat_prices = boat_prices.filter(start_date__lte=q_date_from, end_date__gte=q_date_from)
    #if q_date_to:
    #    boat_prices = boat_prices.filter(start_date__lte=q_date_to, end_date__gte=q_date_to)

    #if q_date_from:
    #    boat_prices = boat_prices.filter(start_date__lte=q_date_from) 
    #if q_date_to:
    #    boat_prices = boat_prices.filter(end_date__gte=q_date_to)
 
    boats = Boat.objects.published()
    if q_boat_types:
        boats = boats.filter(type__in=q_boat_types)

    boats = boats.distinct().order_by('-id')
    p = Paginator(boats, settings.PAGINATOR_BOAT_PER_PAGE).get_page(q_page)
    objects = p.object_list

    q = {
        'boat_types':   q_boat_types,
        'price_from':   q_price_from,
        'price_to':     q_price_to,
        'date_from':    q_date_from,
        'date_to':      q_date_to,
        'price_type':   q_price_type
    }

    f = {
        'boat_types': ', '.join([str(e[1]) for e in Boat.get_types() if e[0] in q_boat_types]),
        'price_type': next((e[1] for e in BoatPrice.get_types() if e[0] == int(q_price_type)), '') if q_price_type else ''
    }

    context = {
        'boats': objects, 
        'boat_types': Boat.get_types(),
        'price_types': BoatPrice.get_types(),
        'q': q, 
        'p': p,
        'f': f
    }

    return render(request, 'boat/boats.html', context=context)   

@login_required
def create(request):
    if request.method == 'GET':
        return render(request, 'boat/create.html', context=get_form_context())

    elif request.method == 'POST':
        data = request.POST
        files = request.FILES.getlist('file')
        prices = json.loads(data.get('prices'))
        
        try:
            if len(files) > FILES_LIMIT_COUNT:
                raise BoatFileCountException()
            
            with transaction.atomic():
                fields = {
                    'name':     data.get('name'),
                    'text':     data.get('text'),
                    'issue_year': data.get('issue_year'),
                    'length':   data.get('length'),
                    'width':    data.get('width'),
                    'draft':    data.get('draft'),
                    'capacity': data.get('capacity'),
                    'type':     data.get('type')
                }
                boat = Boat.objects.create(**fields, owner=request.user)
                if boat.is_motor_boat():
                    motor_boat_fields = {
                        'motor_amount': data.get('motor_amount'),
                        'motor_power': data.get('motor_power')
                    }
                    MotorBoat.objects.create(**motor_boat_fields, boat=boat)

                if boat.is_comfort_boat():
                    comfort_boat_fields = {
                        'berth_amount':     data.get('berth_amount'),
                        'cabin_amount':     data.get('cabin_amount'),
                        'bathroom_amount':  data.get('bathroom_amount')
                    }
                    ComfortBoat.objects.create(**comfort_boat_fields, boat=boat)

                handle_boat_prices(boat, prices)

                for file in files:
                    BoatFile.objects.create(boat=boat, file=file)
        except UnidentifiedImageError:
            return response_invalid_file_type()
        except BoatFileCountException as e:
            return response_files_limit_count(str(e))
        except FileSizeException as e:
            return response_file_limit_size(str(e))
        except ValidationError as e:
            return JsonResponse({'message': list(e)}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'data': {'id': boat.id},
            'redirect': reverse('boat:my_boats')
        })

def booking(request, pk):
    if request.method == 'GET':
        try:
            boat = Boat.objects.published().get(pk=pk)
            price_dates = boat.prices.aggregate(first=Min('start_date'), last=Max('end_date'))
            prices = boat.prices.values('start_date', 'end_date')
            context = {
                'boat': boat,
                'first_price_date': price_dates.get('first'),
                'last_price_date': price_dates.get('last'),
                'prices_exist': price_dates.get('last') is not None and price_dates.get('last') >= timezone.localdate(),
                'price_ranges': [[e['start_date'], e['end_date']] for e in prices]
            }
            return render(request, 'boat/booking.html', context=context)
        except Boat.DoesNotExist:
            return render(request, 'not_found.html')

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
        boat = Boat.objects.get(pk=pk, owner=request.user)
        return render(request, 'boat/view.html', context={'boat': boat})
    except Boat.DoesNotExist:
        return render(request, 'not_found.html')

@login_required
def update(request, pk):
    try:
        boat = Boat.objects.get(pk=pk, owner=request.user)
        
        if request.method == 'GET':
            context = {
                'boat': boat, 
                'prices': serializers.serialize('json', boat.prices.all()),
                **get_form_context()
            }
            return render(request, 'boat/update.html', context=context)
        elif request.method == 'POST':
            data = request.POST
            files = request.FILES.getlist('file')
            prices = json.loads(data.get('prices'))
            
            try:
                if len(files) > FILES_LIMIT_COUNT:
                    raise BoatFileCountException()

                with transaction.atomic():                   
                    boat.name           = data.get('name')
                    boat.text           = data.get('text')
                    boat.issue_year     = data.get('issue_year')
                    boat.length         = data.get('length')
                    boat.width          = data.get('width')
                    boat.draft          = data.get('draft')
                    boat.capacity       = data.get('capacity')
                    boat.type           = data.get('type')
                    if boat.status == Boat.Status.DECLINED:
                        boat.status = Boat.Status.SAVED
                    boat.save()

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

                    handle_boat_prices(boat, prices)

                    BoatDeclinedModeration.objects.filter(boat=boat).delete()
                    BoatFile.objects.filter(boat=boat).exclude(file__in=files).delete()

                    for file in files:
                        BoatFile.objects.get_or_create(boat=boat, file=file)

            except UnidentifiedImageError:
                return response_invalid_file_type()
            except BoatFileCountException as e:
                return response_files_limit_count(str(e))
            except FileSizeException as e:
                return response_file_limit_size(str(e))
            except ValidationError as e:
                return JsonResponse({'message': list(e)}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({'redirect': reverse('boat:my_boats')})
    
    except Boat.DoesNotExist:
        if request.method == 'GET':
            return render(request, 'not_found.html')
        elif request.method == 'POST':
            return response_not_found()


@login_required
@api_view(['POST'])
def delete(request, pk):
    try:
        boat = Boat.objects.get(pk=pk, owner=request.user)
        #if boat.is_read_only:
        #    return JsonResponse({'message': 'Лодку возможно удалить только на статусе "Заготовка"'}, status=status.HTTP_400_BAD_REQUEST)
        boat.delete()
    except Boat.DoesNotExist:
        return response_not_found()
    
    return JsonResponse({'redirect': reverse('boat:my_boats')})

@login_required
def get_files(request, pk):
    files = BoatFile.objects.filter(boat__pk=pk, boat__owner=request.user)
    serializer = BoatFileSerializer(files, many=True, context={'request': request})
    return JsonResponse({'data': serializer.data})