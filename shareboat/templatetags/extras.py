from django import template
from django.conf import settings
from decimal import Decimal

register = template.Library()
_hasattr = hasattr

@register.filter
def hasattr(value, arg):
    return _hasattr(value, arg)

@register.simple_tag
def is_debug():
    return settings.DEBUG

@register.filter
def div(value, arg):
    return str(value / arg).replace(',','.')