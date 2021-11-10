from django import template
from datetime import datetime
from decimal import Decimal

register = template.Library()

@register.filter
def strptime(value, arg):
    return datetime.strptime(value, arg)

@register.filter
def todecimal(value):
    print(value)
    return Decimal(value)