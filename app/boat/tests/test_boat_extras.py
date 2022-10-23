from django.http import QueryDict
from django.test import TestCase

from boat.tests.test_models import create_model, create_simple_boat
from user.tests.test_models import create_boat_owner
from boat.models import Boat, BoatCoordinates, ComfortBoat, Tariff
from boat.templatetags import boat_extras
from base.models import Base

import datetime

class BoatExtrasTestCase(TestCase):

    def setUp(self):
        self.owner = create_boat_owner('admin@admin.ru', '12345')
        self.model = create_model()
        self.boat = create_simple_boat(self.model, self.owner)

    def test_get_boat_coordinates(self):
        self.assertDictEqual(boat_extras.get_boat_coordinates('This is not a boat instance'), {})
        self.assertDictEqual(boat_extras.get_boat_coordinates(self.boat), {})
        
        base = Base.objects.create(name='Base1', lon=111, lat=222, address="Base Address, Moscow, 15", state="Moscow")
        self.boat.base = base 
        self.boat.save()
        self.assertDictEqual(boat_extras.get_boat_coordinates(self.boat), {
            'lat': 222,
            'lon': 111,
            'address': 'Base Address, Moscow, 15',
            'state': 'Moscow'
        })

        self.boat.base = None
        self.boat.save()
        BoatCoordinates.objects.create(boat=self.boat, lon=333, lat=444, address="Boat Address, Moscow, 15", state="Moscow")
        self.assertDictEqual(boat_extras.get_boat_coordinates(self.boat), {
            'lat': 444,
            'lon': 333,
            'address': 'Boat Address, Moscow, 15',
            'state': 'Moscow'
        })

    def test_to_json(self):
        self.assertEqual(boat_extras.to_json({'id': 123, 'sum': 123.45}), '{"id": 123, "sum": 123.45}')

    def test_get_status_color(self):
        self.assertEqual(boat_extras.get_status_color(Boat.Status.SAVED), 'bg-secondary')
        self.assertEqual(boat_extras.get_status_color(Boat.Status.DECLINED), 'bg-danger')
        self.assertEqual(boat_extras.get_status_color(Boat.Status.PUBLISHED), 'bg-success')

    def test_get_list(self):
        d = QueryDict('param1=100&param1=200')
        self.assertListEqual(boat_extras.get_list(d, 'param1'), ['100', '200'])

    def test_get_duration_display(self):
        tariff = Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(2022, 1, 1), end_date=datetime.date(2022, 12, 31),
            name='My Tariff', duration=1, min=1, mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True, price=500
        )
        self.assertEqual(boat_extras.get_duration_display(tariff), 'день')

        tariff.duration = 7
        self.assertEqual(boat_extras.get_duration_display(tariff), '1 неделя')

        tariff.duration = 21
        self.assertEqual(boat_extras.get_duration_display(tariff), '3 недели')

        tariff.duration = 22
        self.assertEqual(boat_extras.get_duration_display(tariff), '22 дня')

    def test_get_min_display(self):
        tariff = Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(2022, 1, 1), end_date=datetime.date(2022, 12, 31),
            name='My Tariff', duration=7, min=1, mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True, price=500
        )     
        self.assertEqual(boat_extras.get_min_display(tariff), 'от 1 недели')   

        tariff.min = 2
        tariff.save()
        self.assertEqual(boat_extras.get_min_display(tariff), 'от 2 недель')

        tariff.duration = 8
        tariff.min = 3
        tariff.save()
        self.assertEqual(boat_extras.get_min_display(tariff), 'от 24 дней')

        tariff.duration = 1
        tariff.min = 1
        tariff.save()
        self.assertEqual(boat_extras.get_min_display(tariff), 'от 1 дня')

    def test_get_berth_amount(self):
        boat = self.boat
        self.assertEqual(boat_extras.get_berth_amount(boat), '-')

        boat.type = Boat.Type.SAILING_YACHT
        comfort_boat = ComfortBoat.objects.create(boat=boat, berth_amount=3, extra_berth_amount=0, cabin_amount=2, bathroom_amount=3)
        self.assertEqual(boat_extras.get_berth_amount(boat), '3')

        comfort_boat.extra_berth_amount = 1
        self.assertEqual(boat_extras.get_berth_amount(boat), '3+1')

        comfort_boat.berth_amount = 0
        self.assertEqual(boat_extras.get_berth_amount(boat), '0+1')
