from decimal import Decimal
import json

from django import template

from booking.models import Booking

register = template.Library()


@register.filter
def get_status_color(value):
    if value == Booking.Status.DECLINED:
        return 'bg-booking-data text-danger'
    if value == Booking.Status.ACCEPTED:
        return 'bg-booking-data text-success'
    return 'bg-booking-data text-secondary'


@register.filter
def spectolist(value):
    try:
        d = json.loads(value)

        for value in d.values():
            value['price'] = Decimal(value['price'])
            value['sum'] = Decimal(value['sum'])

        return list(d.values())
    except (ValueError, TypeError):
        return []


@register.filter
def boatspectoobj(value):
    try:
        d = json.loads(value)

        d['length'] = Decimal(d.get('length'))
        d['width'] = Decimal(d.get('width'))
        d['draft'] = Decimal(d.get('draft'))

        if d.get('motor'):
            d['motor']['motor_power'] = Decimal(d['motor'].get('motor_power'))

        return d
    except (ValueError, TypeError):
        return {}


@register.simple_tag
def get_berth_amount(spec):
    if spec.get('comfort'):
        berth_amount_str = str(spec['comfort'].get('berth_amount'))
        extra_berth_amount_str = ''

        if spec['comfort'].get('extra_berth_amount', 0) > 0:
            extra_berth_amount_str = '+' + \
                str(spec['comfort'].get('extra_berth_amount'))
        return berth_amount_str+extra_berth_amount_str
    return '-'
