import json
from decimal import Decimal

from django import template

from booking.models import Booking

register = template.Library()


@register.filter
def get_status_color(status: Booking.Status) -> str:
    """Получить HTML классы для статуса бронирования.

    Args:
        status: статус бронирования

    Returns:
        str: HTML классы

    """
    mapping = {
        Booking.Status.DECLINED: 'bg-booking-data text-danger',
        Booking.Status.ACCEPTED: 'bg-booking-data text-success'
    }
    return mapping.get(status, 'bg-booking-data text-secondary')


@register.filter
def spectolist(spec: str) -> list:
    """Преобразовать спецификацию JSON в список.

    Args:
        spec: спецификация в формате JSON

    Returns:
        list

    """
    try:
        d = json.loads(spec)

        for value in d.values():
            value['price'] = Decimal(value['price'])
            value['sum'] = Decimal(value['sum'])

        return list(d.values())
    except (ValueError, TypeError):
        return []


@register.filter
def boatspectoobj(value: str) -> dict:
    """Преобразовать спецификацию JSON в словарь.

    Args:
        value: спецификация в формате JSON

    Returns:
        dict

    """
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
def get_berth_amount(spec: dict) -> str:
    """Получить количество спальных мест лодки с учетом доп. мест.

    Args:
        spec: спецификация лодки из бронирования

    Returns:
        str: кол-во спальных мест

    """
    if not spec.get('comfort'):
        return '-'

    berth_amount_str = str(spec['comfort'].get('berth_amount'))
    extra_berth_amount = spec["comfort"].get("extra_berth_amount", 0)
    extra_berth_amount_str = (
        f'+{str(extra_berth_amount)}' if extra_berth_amount > 0 else ''
    )
    return f'{berth_amount_str}{extra_berth_amount_str}'
