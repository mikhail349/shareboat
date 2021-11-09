
from django.shortcuts import render
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse

from rest_framework.decorators import api_view
from rest_framework import status
from PIL import UnidentifiedImageError
from django.core.exceptions import ValidationError
from django.core import serializers

from file.exceptions import FileSizeException

from .exceptions import BoatFileCountException
from .models import Boat, MotorBoat, ComfortBoat, BoatFile, BoatPrice
from .serializers import BoatFileSerializer
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
    return render(request, 'boat/my_boats.html', context={'boats': boats})   

def boats(request):
    boats = Boat.objects.filter(is_published=True)
    if request.user.is_authenticated:
        boats = boats.exclude(owner=request.user)
    return render(request, 'boat/boats.html', context={'boats': boats, 'boat_types': Boat.get_types()})   

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
                    'type':     data.get('type'),
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
            print(boat.length)
            return render(request, 'boat/update.html', context=context)
        elif request.method == 'POST':
            data = request.POST
            files = request.FILES.getlist('file')
            prices = json.loads(data.get('prices'))
            
            try:
                if len(files) > FILES_LIMIT_COUNT:
                    raise BoatFileCountException()

                with transaction.atomic():
                    
                    boat.name   = data.get('name')
                    boat.text   = data.get('text')
                    boat.issue_year = data.get('issue_year')
                    boat.length = data.get('length')
                    boat.width  = data.get('width')
                    boat.draft  = data.get('draft')
                    boat.capacity = data.get('capacity')
                    boat.type   = data.get('type')
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
        boat.delete()
    except Boat.DoesNotExist:
        return response_not_found()
    
    return JsonResponse({'redirect': reverse('boat:my_boats')})

@login_required
def get_files(request, pk):
    files = BoatFile.objects.filter(boat__pk=pk, boat__owner=request.user)
    serializer = BoatFileSerializer(files, many=True, context={'request': request})
    return JsonResponse({'data': serializer.data})