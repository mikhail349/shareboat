from django import template
from booking.models import Booking

register = template.Library()

@register.filter
def get_status_color(value):
    if value == Booking.Status.DECLINED:
        return 'bg-danger text-light'
    if value == Booking.Status.ACCEPTED:
        return 'bg-success text-light'
    return 'bg-secondary text-light'