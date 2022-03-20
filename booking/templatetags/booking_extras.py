from django import template
from booking.models import Booking

register = template.Library()

@register.filter
def get_status_color(value):
    if value == Booking.Status.DECLINED:
        return 'alert-danger'
    if value == Booking.Status.ACCEPTED:
        return 'alert-success'
    return 'alert-secondary'