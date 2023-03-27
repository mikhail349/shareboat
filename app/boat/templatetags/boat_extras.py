import json
from datetime import date as datetime_date
from datetime import datetime
from typing import Any

from django import template
from django.http import HttpRequest, QueryDict

from boat.models import Boat, ComfortBoat, Tariff
from config.utils import get_str_case_by_count

register = template.Library()


@register.filter
def tryiso(value: Any) -> Any:
    """Попытаться перевести значение в iso-format.

    Args:
        value: значение

    Returns:
        Any: в случае успеха строку в формате ISO, иначе входное значение
    """
    if isinstance(value, (datetime_date, datetime)):
        return value.isoformat()
    return value


@register.simple_tag
def get_filter_count(request: HttpRequest) -> int:
    """Получить кол-во примененных фильтров в GET запросе.

    Args:
        request: http-запрос

    Returns:
        int: кол-во

    """
    ex_counters = ('sort', 'page', 'dateFrom')
    return len([
        True for k, v in request.GET.items()
        if k not in ex_counters and v
    ])


@register.simple_tag
def get_boat_coordinates(boat: Boat) -> dict:
    """Получить координаты лодки.

    Args:
        boat: лодка

    Returns:
        dict: пустой словарь или словарь с ключами:
        lat, lon, address, state

    """
    if boat.is_custom_location():
        coordinates = boat.coordinates
    elif boat.base:
        coordinates = boat.base
    else:
        return {}

    res = {
        'lat': coordinates.lat,
        'lon': coordinates.lon,
        'address': coordinates.address,
        'state': coordinates.state
    }

    return res


@register.filter
def to_json(value: Any) -> str:
    """Преобразовать значение в JSON с сериализатором `str`.

    Args:
        value: значение

    Returns:
        str: json

    """
    return json.dumps(value, default=str)


@register.filter
def get_status_color(value: Boat.Status) -> str:
    """Получить CSS-класс фона статуса лодки.

    Args:
        value: статус лодки

    Returns:
        str: CSS-класс

    """
    mapping = {
        Boat.Status.DECLINED: 'bg-danger',
        Boat.Status.PUBLISHED: 'bg-success',
    }
    return mapping.get(value, 'bg-secondary')


@register.filter
def get_list(dictionary: QueryDict, key: str) -> list[str]:
    """Получить значение ключа из строки запроса в виде списка.

    Args:
        dictionary: строка запроса
        key: название параметра

    Returns:
        list[str]: список значений ключа

    """
    return dictionary.getlist(key)


@register.simple_tag
def get_duration_display(tariff: Tariff) -> str:
    """Получить текстовое представление продолжительности тарифа.

    Args:
        tariff: тариф

    Returns:
        str: текстовое представление продолжительности

    """
    if tariff.duration == 1:
        return 'день'
    if tariff.duration % 7 == 0:
        weeks = tariff.duration // 7
        weeks_case = get_str_case_by_count(weeks,
                                           'неделя', 'недели', 'недель')
        return '%s %s' % (weeks, weeks_case)

    duration_case = get_str_case_by_count(tariff.duration,
                                          'день', 'дня', 'дней')
    return f'{str(tariff.duration)} {duration_case}'


@register.simple_tag
def get_min_display(tariff: Tariff) -> str:
    """Получить текстовое представление продолжительности тарифа "от ...".

    Args:
        tariff: тариф

    Returns:
        str: текстовое представление продолжительности

    """
    if tariff.duration % 7 == 0:
        str = get_str_case_by_count(
            tariff.weight // 7, 'недели', 'недель', 'недель'
        )
        return f'от {tariff.weight // 7} {str}'

    str = get_str_case_by_count(tariff.weight, 'дня', 'дней', 'дней')
    return f'от {tariff.weight} {str}'


@register.filter
def daycountcase(value: int) -> str:
    """Получить слово 'день' в правильном падеже в зависимости от кол-ва.

    Args:
        value: кол-во дней

    Returns:
        str: число и слово 'день' в правильном падеже

    """
    value_case = get_str_case_by_count(value, 'день', 'дня', 'дней')
    return f'{value} {value_case}'


@register.simple_tag
def countcase(value: int, one: str, two: str, five: str) -> str:
    """Получить слово в правильном падеже в зависимости от кол-ва.

    Args:
        value: кол-во
        one: вариант слова для '1 X'
        two: вариант слова для '2 X'
        five: вариант слова для '5 X'

    Returns:
        str: слово в правильном падеже

    """
    return get_str_case_by_count(value, one, two, five)


@register.simple_tag
def get_weekdays_display(tariff: Tariff) -> str:
    """Получить дни недели тарифа, перечисленные через запятую.

    Args:
        tariff: тариф

    Returns:
        str: дни тарифа
    """
    weekdays = [tariff.mon, tariff.tue, tariff.wed,
                tariff.thu, tariff.fri, tariff.sat, tariff.sun]

    weekdays_display = ['пн', 'вт', 'ср',
                        'чт', 'пт', 'сб', 'вс']

    return ', '.join(
        [day for i, day in enumerate(weekdays_display) if weekdays[i]]
    )


@register.simple_tag
def get_berth_amount(boat: Boat) -> str:
    """Получить количество спальных мест лодки с учетом доп. мест.

    Args:
        boat: лодка

    Returns:
        str: кол-во спальных мест

    """
    if not boat.is_comfort_boat():
        return '-'

    comfort_boat: ComfortBoat = boat.comfort_boat
    berth_amount_str = str(comfort_boat.berth_amount)
    extra_berth_amount_str = (
        f'+{str(comfort_boat.extra_berth_amount)}'
        if comfort_boat.extra_berth_amount > 0 else ''
    )
    return f'{berth_amount_str}{extra_berth_amount_str}'
