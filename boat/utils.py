from django.http.response import JsonResponse
from django.shortcuts import render
from decimal import Decimal
from boat.exceptions import PriceDateRangeException
from shareboat.date_utils import daterange
from .models import Boat

import json
import decimal 


def calc_booking(boat_pk, start_date, end_date):
    boat = Boat.objects.get(pk=boat_pk)
    prices = boat.prices #for cache
    
    sum = Decimal()
    days = 0
    for date in daterange(start_date, end_date):       
        range_prices = prices.filter(start_date__lte=date, end_date__gte=date)
        if not range_prices:
            raise PriceDateRangeException()
        sum += range_prices[0].price
        days += 1
    return {'sum': float(sum), 'days': days}

def my_boats(request, context=None):
    if context is None:
        context = {}
    boats = Boat.objects.filter(owner=request.user).order_by('id')
    return render(request, 'boat/my_boats.html', context={'boats': boats, 'Status': Boat.Status, **context}) 

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)
