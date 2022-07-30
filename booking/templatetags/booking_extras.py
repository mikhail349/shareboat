from django import template
from booking.models import Booking

import json
from decimal import Decimal

register = template.Library()

@register.filter
def get_status_color(value):
    if value == Booking.Status.DECLINED:
        return 'bg-light text-danger'
    if value == Booking.Status.ACCEPTED:
        return 'bg-light text-success'
    return 'bg-light text-secondary'


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