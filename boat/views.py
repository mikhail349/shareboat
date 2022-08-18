from decimal import Decimal
from django.shortcuts import redirect, render
from django.db import transaction
from django.db.models import Max, Min, Value
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
from boat.forms import TariffForm, TermForm
from notification import utils as notify

from .models import Boat, BoatFav, Manufacturer, Model, MotorBoat, ComfortBoat, BoatFile, BoatCoordinates, Tariff, Term
from .serializers import BoatFileSerializer, ModelSerializer
from .utils import calc_booking as _calc_booking
from base.models import Base
from booking.models import Booking
from chat.models import MessageBoat

import json
import datetime

def response_not_found():
    return JsonResponse({'message': 'Лодка не найдена'}, status=404)

def get_form_context(request):
    return {
        'boat_types': Boat.get_types(), 
        'motor_boat_types': json.dumps(Boat.get_motor_boat_types()),
        'comfort_boat_types': json.dumps(Boat.get_comfort_boat_types()),
        'bases': Base.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
        'terms': Term.objects.filter(user=request.user).order_by('name')
    }

def get_bool(value):
    if value in (True, 'True', 'true', '1', 'on'):
        return True
    return False

FILES_LIMIT_COUNT = 30

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

    boats = Boat.published.filter(favs__user=request.user).prefetch_actual_tariffs().annotate(in_fav=Value(True)).order_by('id')
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
            return render(request, 'boat/moderate.html', context=context, status=404) 
        
        boat.status = Boat.Status.PUBLISHED
        boat.save()
        notify.send_boat_published_to_owner(boat, request)
        return redirect(reverse('boat:boats_on_moderation'))
    except Boat.DoesNotExist:
        return render(request, 'not_found.html', status=404)

@permission_required('boat.moderate_boats', raise_exception=True)
def reject(request, pk):
    if request.method == 'POST':
        try:
            boat = Boat.objects.get(pk=pk, status=Boat.Status.ON_MODERATION)
            #reason = int(request.POST.get('reason'))
            comment = request.POST.get('comment')
            modified = parse_datetime(request.POST.get('modified'))
                   
            reasons = MessageBoat.get_rejection_reasons()

            if boat.modified != modified:
                context = {
                    'boat': boat,
                    'reasons': reasons,
                    'errors': 'Лодка была изменена. Возможно, недочёты исправлены.'
                }
                return render(request, 'boat/moderate.html', context=context, status=404) 
            
            boat.status = Boat.Status.DECLINED
            boat.save()

            #reason_display = [item[1] for item in reasons if item[0] == reason][0]
            notify.send_boat_declined_to_owner(boat, comment, request)

            return redirect(reverse('boat:boats_on_moderation'))
        except Boat.DoesNotExist:
            return render(request, 'not_found.html', status=404)

def search_boats(request):
    date = datetime.datetime.now().date()
    q_date_from = request.GET.get('dateFrom')
    q_date_to   = request.GET.get('dateTo') 
    q_boat_types=[int(e) for e in request.GET.getlist('boatType')]
    q_sort = request.GET.get('sort', 'sum_asc')
    q_page = request.GET.get('page', 1)
    q_state = request.GET.get('state')
    q_price_from = Decimal(request.GET.get('priceFrom')) if request.GET.get('priceFrom') else None
    q_price_to = Decimal(request.GET.get('priceTo')) if request.GET.get('priceTo') else None

    boats = Boat.published.all()
    if q_date_from and q_date_to:
        q_date_from = datetime.datetime.strptime(q_date_from, '%Y-%m-%d')
        q_date_to = datetime.datetime.strptime(q_date_to, '%Y-%m-%d')    
      
        boats = boats.filter(tariffs__start_date__lte=q_date_from, tariffs__end_date__gte=q_date_to).distinct()
        boats = boats.exclude(bookings__in=Booking.objects.blocked_in_range(q_date_from, q_date_to))
    else:
        boats = boats.filter(tariffs__end_date__gte=date).distinct()
    
    if q_boat_types:
        boats = boats.filter(type__in=q_boat_types)  

    boats = boats.annotate_in_fav(user=request.user) 
    boats = boats.prefetch_actual_tariffs()

    if q_state:
        boats = boats.filter(coordinates__state=q_state).union(boats.filter(base__state=q_state)) 

    if q_price_from:
        boats = [boat for boat in boats if boat.actual_tariffs[0].price_per_day >= q_price_from]

    if q_price_to:
        boats = [boat for boat in boats if boat.actual_tariffs[0].price_per_day <= q_price_to]

    boats = sorted(boats, key=lambda boat: boat.actual_tariffs[0].price_per_day, reverse=q_sort.split('_')[1]=='desc')
    p = Paginator(boats, settings.PAGINATOR_BOAT_PER_PAGE).get_page(q_page)

    boats_states = set(Boat.published.filter(coordinates__pk__isnull=False).values_list('coordinates__state', flat=True))
    bases_states = set(Boat.published.filter(base__pk__isnull=False).values_list('base__state', flat=True))
    states = sorted(boats_states | bases_states)

    context = {
        'sort_list': [('sum_asc', 'Сначала дешевые'), ('sum_desc', 'Сначала дорогие')],
        'boat_types': Boat.get_types(),
        'boats': p.object_list,
        'p': p,
        'states': states
    }

    return render(request, 'boat/search_boats.html', context)


def switch_fav(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'data': 'redirect', 'url': reverse('user:login')}, status=302)

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
            tariffs = boat.tariffs.filter(active=True)
            price_dates = tariffs.aggregate(first=Min('start_date'), last=Max('end_date'))
            prices = tariffs.values('start_date', 'end_date')
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
    res = _calc_booking(pk, start_date, end_date)
    return JsonResponse(res)

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
            **get_form_context(request)
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
                **get_form_context(request)
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
    if boat.bookings.filter(status__in=[Booking.Status.ACCEPTED, Booking.Status.PREPAYMENT_REQUIRED, Booking.Status.ACTIVE]).exists():
        return JsonResponse({'message': "По этой лодке уже есть подтвержденные или активные бронирования", "code": "invalid_status"}, status=status.HTTP_400_BAD_REQUEST)    

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
    is_custom_location = get_bool(data.get('is_custom_location'))
    prepayment_required = get_bool(data.get('prepayment_required'))
    base = Base.objects.get(pk=data.get('base')) if data.get('base') and not is_custom_location else None

    try:
        term = Term.objects.get(pk=data.get('term'), user=request.user) if data.get('term') else None

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
                boat.term       = term
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
                    'term':         term,
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
                    comfort_boat.berth_amount       = data.get('berth_amount')
                    comfort_boat.extra_berth_amount = data.get('extra_berth_amount')
                    comfort_boat.cabin_amount       = data.get('cabin_amount')
                    comfort_boat.bathroom_amount    = data.get('bathroom_amount')
                    comfort_boat.save()
                except ComfortBoat.DoesNotExist:
                    comfort_boat_fields = {
                        'berth_amount':         data.get('berth_amount'),
                        'extra_berth_amount':   data.get('extra_berth_amount'),
                        'cabin_amount':         data.get('cabin_amount'),
                        'bathroom_amount':      data.get('bathroom_amount')
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

            BoatFile.objects.filter(boat=boat).exclude(file__in=files).delete()
            for file in files:
                BoatFile.objects.get_or_create(boat=boat, file=file)

            return JsonResponse({
                'data': {'id': boat.id},
                'redirect': reverse('boat:my_boats')
            })

    except Boat.DoesNotExist:
        return response_not_found()
    except Term.DoesNotExist:
        return JsonResponse({'message': 'Условия аренды не найдены'}, status=404)
    except ValidationError as e:
        return JsonResponse({'message': list(e)}, status=status.HTTP_400_BAD_REQUEST)
 
def redirect_to_tariffs(boat_pk):
    return redirect(reverse('boat:view', kwargs={'pk': boat_pk}) + '#tariffs')

@login_required
@permission_required('boat.add_tariff', raise_exception=True)
def create_tariff(request):
    if request.method == 'GET':
        initial = {
            'boat': request.GET.get('boat_pk'),
        }
        form = TariffForm(initial=initial)
        return render(request, 'boat/create_tariff.html', context={'form': form})
    elif request.method == 'POST':
        form = TariffForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect_to_tariffs(form.instance.boat.pk)
        return render(request, 'boat/create_tariff.html', context={'form': form}, status=400)

@login_required
@permission_required('boat.change_tariff', raise_exception=True)
def update_tariff(request, pk):
    if request.method == 'GET':
        try:
            tariff = Tariff.objects.get(pk=pk, boat__owner=request.user)
            form = TariffForm(instance=tariff)
            return render(request, 'boat/update_tariff.html', context={'form': form})
        except Tariff.DoesNotExist:
            return render(request, 'not_found.html', status=404)
    elif request.method == 'POST':
        try:
            tariff = Tariff.objects.get(pk=pk, boat__owner=request.user)
            form = TariffForm(request.POST, instance=tariff, request=request)
            if form.is_valid():
                form.save()
                return redirect_to_tariffs(form.instance.boat.pk)
            return render(request, 'boat/update_tariff.html', context={'form': form}, status=400)
        except Tariff.DoesNotExist:
            return response_not_found()

@login_required
@permission_required('boat.delete_tariff', raise_exception=True)
def delete_tariff(request, pk):
    try:
        tariff = Tariff.objects.get(pk=pk, boat__owner=request.user)
        tariff.delete()
        return redirect_to_tariffs(tariff.boat.pk)
    except Tariff.DoesNotExist:
        return response_not_found()

@login_required
@permission_required('boat.add_term', raise_exception=True)
def create_term(request):
      
    if request.method == 'GET':
        is_popup = get_bool(request.GET.get('is_popup', False))
        form = TermForm()
        if is_popup:
            return render(request, 'boat/popup_create_term.html', context={'form': form})
    elif request.method == 'POST':
        is_popup = get_bool(request.POST.get('is_popup', False))
        form = TermForm(request.POST)
        if form.is_valid():
            term = form.save(commit=False)
            term.user = request.user
            term.save()
            if is_popup:
                data_json = json.dumps({"pk": form.instance.pk , "name": form.instance.name}) 
                return render(request, 'popup_response.html', context={'content': data_json})
            return redirect('/')
        if is_popup:
            return render(request, 'boat/popup_create_term.html', context={'form': form}, status=400)