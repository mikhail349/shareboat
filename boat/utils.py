from datetime import timedelta
from decimal import Decimal
from boat.exceptions import PriceDateRangeException
from shareboat.date_utils import daterange
from .models import Boat, BoatPrice, Tariff

from django.db.models import Q

def _calc_booking(boat_pk, start_date, end_date):
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


def calc_booking(boat_pk, start_date, end_date):
    class TariffNotFound(Exception):
        pass
    class Node:
        def __init__(self, duration, price, prev=None):
            self.duration = duration
            self.price = price
            self.prev = prev

    def _return_empty():
        return {}
    
    def is_weekday_in_tariff(weekday, tariff):
        if weekday == 0:
            return tariff.mon
        if weekday == 1:
            return tariff.tue
        if weekday == 2:
            return tariff.wed
        if weekday == 3:
            return tariff.thu
        if weekday == 4:
            return tariff.fri
        if weekday == 5:
            return tariff.sat
        if weekday == 6:
            return tariff.sun
        return None
    
    try:
        boat = Boat.objects.get(pk=boat_pk)
    except Boat.DoesNotExist:
        return _return_empty()    

    tariffs = list(boat.tariffs.filter(active=True).exclude(Q(end_date__lt=start_date) | Q(start_date__gt=end_date)))
    used_tariffs = {}
    total_sum = Decimal("0.0")
    date = start_date
    node = None

    check_min_duration = True
    last_tariff = None
    try:
        while date < end_date:
            filtered = [item for item in tariffs if item.start_date <= date <= item.end_date and is_weekday_in_tariff(date.weekday(), item)]
            weighted = sorted(filtered, key=lambda tariff: tariff.weight, reverse=True)

            if not weighted and last_tariff:
                weighted = [last_tariff]

            date_changed = False
            for tariff in weighted:
                target_duration = (end_date - date).days

                if last_tariff != tariff:
                    if target_duration < tariff.min_duration:
                        continue  
                    check_min_duration = True
                
                if check_min_duration:
                    duration = tariff.min_duration
                    price = tariff.min_price
                    check_min_duration = False
                else:
                    duration = tariff.duration
                    price = tariff.price

                if target_duration < duration:
                    continue

                if used_tariffs.get(date, 0) == tariff.pk:
                    continue

                node = Node(duration, price, node)
                used_tariffs[date] = tariff.pk
                total_sum += price
                date += timedelta(days=duration)
                date_changed = True
                last_tariff = tariff
                break

            if not date_changed:
                if node:                   
                    total_sum -= node.price
                    date -= timedelta(days=node.duration)
                    node = node.prev
                else:
                    raise TariffNotFound()

    except TariffNotFound:
        return _return_empty()

    return {'sum': float(total_sum), 'days': (end_date - start_date).days}