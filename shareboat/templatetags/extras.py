from django import template
from django.conf import settings

register = template.Library()
_hasattr = hasattr

@register.filter
def hasattr(value, arg):
    return _hasattr(value, arg)

@register.simple_tag
def is_debug():
    return settings.DEBUG