from django import template
from booking.models import Booking

register = template.Library()

@register.filter
def get_status_color(value):
    if value == Booking.Status.DECLINED:
        return 'bg-light text-danger'
    if value == Booking.Status.ACCEPTED:
        return 'bg-light text-success'
    return 'bg-light text-secondary'