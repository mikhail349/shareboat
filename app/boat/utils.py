from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q

from .models import Boat, Tariff


def calc_booking(boat_pk: int, start_date: date, end_date: date) -> dict:
    """Рассчитать стоимость бронирования.

    Args:
        boat_pk: ID лодки
        start_date: дата начала бронирования
        end_date: дата окончания бронирования

    Returns:
        dict: пустой словарь или содержащий
        ```
        sum - итоговую стоимость
        days - кол-во дней
        spec - спецификация бронирования
        ```

    """
    class TariffNotFoundError(Exception):
        """Ошибка - тариф не найден."""

    class Node:
        """Класс ноды тарифа."""
        def __init__(self, tariff, prev=None):
            self.tariff = tariff
            self.prev = prev

    def _return_empty() -> dict:
        """Вернуть пустой словарь.

        Returns:
            dict

        """
        return {}

    def is_weekday_in_tariff(weekday, tariff: Tariff) -> bool:
        """Есть ли день недели в тарифе.

        Args:
            weekday: день недели, начиная с 0
            tariff: тариф
        """
        mapping = {
            0: tariff.mon,
            1: tariff.tue,
            2: tariff.wed,
            3: tariff.thu,
            4: tariff.fri,
            5: tariff.sat,
            6: tariff.sun,
        }
        return mapping.get(weekday)

    def spec_inc(tariff: Tariff):
        """Добавить тариф в спецификацию бронирования.

        Args:
            tariff: тариф

        """
        item = spec.get(tariff.pk, {})
        item['name'] = tariff.name
        item['price'] = tariff.price
        item['amount'] = item.get('amount', 0) + 1
        item['sum'] = item.get('sum', Decimal("0.0")) + tariff.price
        spec[tariff.pk] = item

    def spec_dec(tariff: Tariff):
        """Исключить тариф из спецификации бронирования.

        Args:
            tariff: тариф

        """
        item = spec.get(tariff.pk)
        item['amount'] = item['amount'] - 1
        item['sum'] = item['sum'] - tariff.price

        if item['amount'] == 0:
            return spec.pop(tariff.pk)
        spec[tariff.pk] = item

    def is_last_tariff_ok() -> bool:
        """Попадает ли последний обработанный тариф в текущую дату.

        Returns:
            bool

        """
        if last_tariff:
            if last_tariff.start_date <= date <= last_tariff.end_date:
                return True
        return False

    try:
        boat = Boat.objects.get(pk=boat_pk)
    except Boat.DoesNotExist:
        return _return_empty()

    total_duration = (end_date - start_date).days
    tariffs = list(
        boat.tariffs.filter(
            active=True, weight__lte=total_duration
        ).exclude(
            Q(end_date__lt=start_date) | Q(start_date__gt=end_date)
        )
    )
    used_tariffs = {}
    total_sum = Decimal("0.0")
    date = start_date
    node = None
    last_tariff = None
    spec = {}

    try:
        while date < end_date:
            filtered = [
                tariff for tariff in tariffs
                if tariff.start_date <= date <= tariff.end_date
            ]
            weighted = sorted(
                filtered, key=lambda tariff: tariff.weight, reverse=True)

            date_changed = False
            for i, tariff in enumerate(weighted):
                if not is_weekday_in_tariff(date.weekday(), tariff):
                    if i == len(weighted) - 1 and is_last_tariff_ok():
                        tariff = last_tariff
                    else:
                        continue

                target_duration = (end_date - date).days

                if target_duration < tariff.duration:
                    continue

                if used_tariffs.get(date, 0) == tariff.pk:
                    continue

                node = Node(tariff, node)
                used_tariffs[date] = tariff.pk
                total_sum += tariff.price
                date += timedelta(days=tariff.duration)
                spec_inc(tariff)

                date_changed = True
                last_tariff = tariff
                break

            if not date_changed:
                if node:
                    total_sum -= node.tariff.price
                    date -= timedelta(days=node.tariff.duration)
                    spec_dec(node.tariff)
                    node = node.prev
                else:
                    raise TariffNotFoundError()

    except TariffNotFoundError:
        return _return_empty()

    return {
        'sum': total_sum,
        'days': (end_date - start_date).days,
        'spec': spec
    }
