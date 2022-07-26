from datetime import timedelta
from decimal import Decimal
from .models import Boat

from django.db.models import Q


def calc_booking(boat_pk, start_date, end_date):
    
    class TariffNotFound(Exception):
        pass
    
    class Node:
        def __init__(self, tariff, prev=None):
            self.tariff = tariff
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

    total_duration = (end_date - start_date).days
    tariffs = list(boat.tariffs.filter(active=True, weight__lte=total_duration).exclude(Q(end_date__lt=start_date) | Q(start_date__gt=end_date)))
    used_tariffs = {}
    total_sum = Decimal("0.0")
    date = start_date
    node = None
    last_tariff = None
    
    try:
        while date < end_date:
            filtered = [item for item in tariffs if item.start_date <= date <= item.end_date and is_weekday_in_tariff(date.weekday(), item)]
            weighted = sorted(filtered, key=lambda tariff: tariff.weight, reverse=True)

            if not weighted and last_tariff:
                if last_tariff.start_date <= date <= last_tariff.end_date:
                    weighted = [last_tariff]

            date_changed = False
            for tariff in weighted:
                target_duration = (end_date - date).days

                if target_duration < tariff.duration:
                    continue

                if used_tariffs.get(date, 0) == tariff.pk:
                    continue

                node = Node(tariff, node)
                used_tariffs[date] = tariff.pk
                total_sum += tariff.price
                date += timedelta(days=tariff.duration)
                date_changed = True
                last_tariff = tariff
                break

            if not date_changed:
                if node:                   
                    total_sum -= node.tariff.price
                    date -= timedelta(days=node.tariff.duration)
                    node = node.prev
                else:
                    raise TariffNotFound()

    except TariffNotFound:
        return _return_empty()

    return {'sum': total_sum, 'days': (end_date - start_date).days}