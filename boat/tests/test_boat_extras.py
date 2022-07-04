from decimal import Decimal
from django.http import QueryDict
from django.test import TestCase

from boat.tests.test_models import create_model, create_simple_boat
from user.tests.test_models import create_boat_owner
from boat.models import Boat, BoatCoordinates, BoatPrice
from boat.templatetags import boat_extras
from base.models import Base

import datetime

class BoatExtrasTest(TestCase):

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

    def test_get_min_actual_price(self):
        now = datetime.datetime.now()
        BoatPrice.objects.create(boat=self.boat, start_date=datetime.date(now.year-1, 1, 1), end_date=datetime.date(now.year-1, 12, 31), price=100)

        self.assertIsNone(boat_extras.get_min_actual_price(self.boat))

        BoatPrice.objects.create(boat=self.boat, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 12, 31), price=100)
        BoatPrice.objects.create(boat=self.boat, start_date=datetime.date(now.year+1, 1, 1), end_date=datetime.date(now.year+1, 12, 31), price=90)

        self.assertEqual(boat_extras.get_min_actual_price(self.boat), Decimal('100.00'))
