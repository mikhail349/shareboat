from django import template
from datetime import datetime
from decimal import Decimal
import json
from boat.utils import DecimalEncoder

from boat.models import BoatPrice, Boat

register = template.Library()

@register.simple_tag
def get_boat_coordinates(boat):
    if boat.is_custom_location():
        coordinates = boat.coordinates
    elif boat.base:
        coordinates = boat.base
    else:
        return '{}'

    res = {
        'lat': coordinates.lat,
        'lon': coordinates.lon,
        'address': coordinates.address,
        'state': coordinates.state
    }        

    return json.dumps(res, cls=DecimalEncoder)

@register.filter
def strptime(value, arg):
    return datetime.strptime(value, arg)

@register.filter
def todecimal(value):
    return Decimal(value)

@register.filter
def toaccusative(value):
    d = {
        'неделя': 'неделю'
    }
    return d.get(value.lower(), value)

@register.filter
def get_status_color(value):
    if value == Boat.Status.DECLINED:
        return 'bg-danger'
    if value == Boat.Status.PUBLISHED:
        return 'bg-success'
    return 'bg-secondary'

@register.simple_tag
def calc_sum(boat, *args, **kwargs):
    if kwargs.get('start_date') and kwargs.get('end_date'):
        start_date  = datetime.strptime(kwargs.get('start_date'), '%Y-%m-%d')
        end_date    = datetime.strptime(kwargs.get('end_date'), '%Y-%m-%d')
        total_days  = (end_date - start_date).days + 1
        weeks       = total_days // 7
        days        = total_days - (weeks * 7)
        
        boat_prices = BoatPrice.objects.filter(boat=boat, start_date__lte=start_date, end_date__gte=end_date)
        try:
            pass
            #week_price  = boat_prices.get()
        except BoatPrice.DoesNotExist:
            pass

    return None