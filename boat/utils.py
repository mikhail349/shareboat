from decimal import Decimal
from boat.exceptions import PriceDateRangeException
from shareboat.date_utils import daterange
from .models import BoatPrice


def calc_booking(boat_pk, start_date, end_date):
    prices = BoatPrice.objects.filter(boat__pk=boat_pk)

    sum = Decimal()
    days = 0
    for date in daterange(start_date, end_date):       
        range_prices = prices.filter(start_date__lte=date, end_date__gte=date)
        if not range_prices:
            raise PriceDateRangeException()
        sum += range_prices[0].price
        days += 1
    return {'sum': float(sum), 'days': days}