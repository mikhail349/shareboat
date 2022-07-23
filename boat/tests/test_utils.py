from decimal import Decimal
from django.test import TestCase
from boat.exceptions import PriceDateRangeException

from boat.tests.test_models import create_model, create_simple_boat
from user.tests.test_models import create_boat_owner

from boat.models import BoatPrice, Tariff
from boat.utils import calc_booking, calc_booking_v2

import datetime

class UtilsTestCase(TestCase):

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

    def test_calc_booking_v2(self):
        YEAR = 2022

        def _sum(from_day, to_day):
            res = calc_booking_v2(self.boat, start_date=datetime.date(YEAR, 7, from_day), end_date=datetime.date(YEAR, 7, to_day))
            if not res:
                return None
            return res.get('sum')
        
        # case 1
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Неделя',
            duration=7,
            min=1,   
            
            tue=True,
            wed=True,
            thu=True,
            price=8_000
        )
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Суточно 3+',
            duration=1,
            min=3,  

            mon=True,
            tue=True,
            wed=True,
            thu=True,
            fri=True,
            sat=True,
            sun=True,
            price=500
        )

        self.assertEqual(_sum(7,9), None)
        self.assertEqual(_sum(7,10), 1_500)
        self.assertEqual(_sum(7,11), 2_000)
        self.assertEqual(_sum(7,12), 2_500)
        self.assertEqual(_sum(7,13), 3_000)
        self.assertEqual(_sum(7,14), 8_000) # !
        self.assertEqual(_sum(7,15), 4_000)
        self.assertEqual(_sum(7,20), 8_000 + 3_000)
        self.assertEqual(_sum(7,21), 16_000)
        self.assertEqual(_sum(7,22), 8_000 + 4_000)

        # case 2
        Tariff.objects.all().delete()
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Неделя',
            duration=7,
            min=1,   
            
            thu=True,
            price=8_000
        )
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Выходные',
            duration=3,
            min=1,  

            fri=True,
            price=2_000
        )
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Суточно',
            duration=1,
            min=1,  

            mon=True,
            tue=True,
            wed=True,
            thu=True,
            fri=True,
            sat=True,
            sun=True,
            price=500
        )

        self.assertEqual(_sum(7,14), 8_000)
        self.assertEqual(_sum(7,15), 8_500)
        self.assertEqual(_sum(7,16), 9_000)
        self.assertEqual(_sum(7,17), 9_500)
        self.assertEqual(_sum(7,18), 10_500) 
