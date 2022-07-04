from decimal import Decimal
from django.test import TestCase
from boat.exceptions import PriceDateRangeException

from boat.tests.test_models import create_model, create_simple_boat
from user.tests.test_models import create_boat_owner

from boat.models import BoatPrice
from boat.utils import calc_booking

import datetime

class UtilsTest(TestCase):

    def setUp(self):
        owner = create_boat_owner('owner@mail.ru', '12345')
        model = create_model()
        self.boat = create_simple_boat(model, owner)
    
    def test_calc_booking(self):
        now = datetime.datetime.now()
        BoatPrice.objects.create(boat=self.boat, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 1, 31), price=100)
        
        res = calc_booking(self.boat.pk, start_date=datetime.date(now.year, 1, 5), end_date=datetime.date(now.year, 1, 8)) 
        self.assertDictEqual(res, {'sum': 400.0, 'days': 4})

        with self.assertRaises(PriceDateRangeException):
            calc_booking(self.boat.pk, start_date=datetime.date(now.year, 2, 1), end_date=datetime.date(now.year, 2, 10)) 