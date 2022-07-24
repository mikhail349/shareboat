from django import template
from django.db.models import Q

from datetime import datetime
import json
from boat.models import BoatPrice, Boat, Tariff
from django.utils.dateparse import parse_date

register = template.Library()

@register.simple_tag
def get_boat_coordinates(boat):
    if not isinstance(boat, Boat):
        return {}
    if boat.is_custom_location():
        coordinates = boat.coordinates
    elif boat.base:
        coordinates = boat.base
    else:
        return {}

    res = {
        'lat': coordinates.lat,
        'lon': coordinates.lon,
        'address': coordinates.address,
        'state': coordinates.state
    }   

    return res

@register.filter
def to_json(value):
    return json.dumps(value, default=str)

@register.filter
def get_status_color(value):
    if value == Boat.Status.DECLINED:
        return 'bg-danger'
    if value == Boat.Status.PUBLISHED:
        return 'bg-success'
    return 'bg-secondary'

@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key)

@register.simple_tag
def get_min_actual_price(boat):
    tariffs = Tariff.objects.filter(boat=boat).active_gte_now().order_by('start_date', 'duration')
    if tariffs:
        price = tariffs[0].price
        if tariffs[0].duration == 1:
            duration = 'день'
        elif tariffs[0].duration == 7:
            duration = 'неделя'
        else:
            duration = f'{str(tariffs[0].duration)} дн.'

        return {'price': price, 'duration': duration}
    return None

@register.simple_tag
def get_weekdays_display(tariff):
    def _get_display(weekday):
        if weekday == 0: return 'пн'
        if weekday == 1: return 'вт'
        if weekday == 2: return 'ср'
        if weekday == 3: return 'чт'
        if weekday == 4: return 'пт'
        if weekday == 5: return 'сб'
        if weekday == 6: return 'вс'

    l = [tariff.mon, tariff.tue, tariff.wed, tariff.thu, tariff.fri, tariff.sat, tariff.sun]
    
    res = ''
    for i in range(len(l)):
        if l[i]:
            res += ', ' + _get_display(i)
    return res[2:]