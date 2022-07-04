from django import template
from django.db.models import Q

from datetime import datetime
from decimal import Decimal
import json
from boat.utils import DecimalEncoder, calc_booking as _calc_booking 
from boat.models import BoatPrice, Boat
from boat.exceptions import PriceDateRangeException
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
    return json.dumps(value, cls=DecimalEncoder)

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
    now = datetime.now()
    prices = BoatPrice.objects.filter(boat=boat).filter(Q(start_date__lte=now, end_date__gte=now) | Q(start_date__gt=now)).order_by('start_date')
    if prices:
        return prices[0].price
    return None