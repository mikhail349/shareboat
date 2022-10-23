from datetime import date as datetime_date, datetime
import json

from django import template

from boat.models import Boat
from config.utils import get_str_case_by_count

register = template.Library()


@register.filter
def tryiso(value):
    if isinstance(value, (datetime_date, datetime)):
        return value.isoformat()
    return value


@register.simple_tag
def get_filter_count(request):
    ex_counters = ('sort', 'page', 'dateFrom')
    return len([
        True for k, v in request.GET.items()
        if k not in ex_counters and v
    ])


@register.simple_tag
def get_boat_coordinates(boat):
    if not isinstance(boat, Boat):
        return {}
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
def to_json(value):
    return json.dumps(value, default=str)


@register.filter
def get_status_color(value):
    if value == Boat.Status.DECLINED:
        return 'bg-danger'
    if value == Boat.Status.PUBLISHED:
        return 'bg-success'
    return 'bg-secondary'


@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key)


@register.simple_tag
def get_duration_display(tariff):
    if tariff.duration == 1:
        return 'день'
    elif tariff.duration % 7 == 0:
        weeks = tariff.duration // 7
        weeks_case = get_str_case_by_count(weeks,
                                           'неделя', 'недели', 'недель')
        return '%s %s' % (weeks, weeks_case)

    duration_case = get_str_case_by_count(tariff.duration,
                                          'день', 'дня', 'дней')
    return f"{str(tariff.duration)} {duration_case}"


@register.simple_tag
def get_min_display(tariff):
    if tariff.duration % 7 == 0:
        str = get_str_case_by_count(
            tariff.weight // 7, 'недели', 'недель', 'недель')
        return f'от {tariff.weight // 7} {str}'
    else:
        str = get_str_case_by_count(tariff.weight, 'дня', 'дней', 'дней')
        return f'от {tariff.weight} {str}'


@register.filter
def daycountcase(value):
    value_case = get_str_case_by_count(value, 'день', 'дня', 'дней')
    return '%s %s' % (value, value_case)


@register.simple_tag
def countcase(value, one, two, five):
    return get_str_case_by_count(value, one, two, five)


@register.simple_tag
def get_weekdays_display(tariff):
    def _get_display(weekday):
        if weekday == 0:
            return 'пн'
        if weekday == 1:
            return 'вт'
        if weekday == 2:
            return 'ср'
        if weekday == 3:
            return 'чт'
        if weekday == 4:
            return 'пт'
        if weekday == 5:
            return 'сб'
        if weekday == 6:
            return 'вс'

    weekdays = [tariff.mon, tariff.tue, tariff.wed,
                tariff.thu, tariff.fri, tariff.sat, tariff.sun]

    res = ''
    for i in range(len(weekdays)):
        if weekdays[i]:
            res += ', ' + _get_display(i)
    return res[2:]


@register.simple_tag
def get_berth_amount(boat):
    if boat.is_comfort_boat():
        berth_amount_str = str(boat.comfort_boat.berth_amount)
        extra_berth_amount_str = ''
        if boat.comfort_boat.extra_berth_amount > 0:
            extra_berth_amount_str = '+' + \
                str(boat.comfort_boat.extra_berth_amount)
        return berth_amount_str+extra_berth_amount_str
    return '-'
