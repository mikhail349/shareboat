from datetime import datetime, timedelta
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


def calc_booking_v2(boat, start_date, end_date):
    class TariffNotFound(Exception):
        pass
    
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

    tariffs = list(boat.tariffs.all())
    used_tariffs = []

    total_sum = Decimal("0.0")
    date = start_date

    try:
        while date < end_date:
            print(date)
            filtered = [item for item in tariffs if item.start_date <= date <= item.end_date and is_weekday_in_tariff(date.weekday(), item)]
            weighted = sorted(filtered, key=lambda tariff: tariff.weight, reverse=True)

            date_enter = date

            for tariff in weighted:

                min_duration = tariff.duration * tariff.min
                max_duration = tariff.duration * tariff.max if tariff.max else None
                target_duration = (end_date - date).days

                if tariff.pk in used_tariffs:
                    continue

                if target_duration < min_duration:
                    continue

                if tariff.max and target_duration > max_duration:
                    used_tariffs.append(tariff.pk)
                    total_sum += (tariff.max * tariff.price)
                    date += timedelta(days=max_duration)
                    break

                if min_duration <= target_duration and (tariff.max is None or target_duration <= max_duration):
                    multiplicity = target_duration // tariff.duration
                    total_sum += (Decimal(multiplicity) * tariff.price)
                    date += timedelta(days=multiplicity * tariff.duration)
                    break

                raise TariffNotFound()

            if date_enter == date:
                raise TariffNotFound()
    except TariffNotFound:
        return {}

    return {'sum': float(total_sum), 'days': (end_date - start_date).days}