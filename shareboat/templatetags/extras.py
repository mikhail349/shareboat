from django import template

register = template.Library()
_hasattr = hasattr

@register.filter
def hasattr(value, arg):
    return _hasattr(value, arg)
