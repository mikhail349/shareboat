from django import template
from notification.models import BoatDeclinedModeration

register = template.Library()
_hasattr = hasattr

@register.filter
def hasattr(value, arg):
    return _hasattr(value, arg)
