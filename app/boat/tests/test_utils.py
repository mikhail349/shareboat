import datetime

from django.test import TestCase

from boat.models import Tariff
from boat.tests.test_models import create_model, create_simple_boat
from boat.utils import calc_booking
from user.tests.test_models import create_boat_owner


class UtilsTestCase(TestCase):

    def setUp(self):
        owner = create_boat_owner('owner@mail.ru', '12345')
        model = create_model()
        self.boat = create_simple_boat(model, owner)

    def test_calc_booking(self):
        YEAR = 2022

        def _sum(from_day, to_day):
            res = calc_booking(self.boat.pk, start_date=datetime.date(YEAR, 7, from_day), end_date=datetime.date(YEAR, 7, to_day))
            if not res:
                return None
            return res.get('sum')

        # boat not found
        res = calc_booking(0, start_date=datetime.date(YEAR, 7, 1), end_date=datetime.date(YEAR, 7, 3))
        self.assertDictEqual(res, {})
        
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
        self.assertEqual(_sum(7,14), 8_000) 
        self.assertEqual(_sum(7,15), 8_500)
        self.assertEqual(_sum(7,20), 8_000 + 3_000)
        self.assertEqual(_sum(7,21), 16_000)
        self.assertEqual(_sum(7,22), 16_500)

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

        # case 3
        Tariff.objects.all().delete()
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Суточно',
            duration=1,
            min=1,  

            mon=True,
            price=500
        )
        
        self.assertEqual(_sum(4,6), 1_000)

        # case 4
        Tariff.objects.all().delete()
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Неделя',
            duration=7,
            min=1,   
            
            tue=True,
            wed=True,
            thu=True,
            price=150
        )
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Выходные',
            duration=3,
            min=1,  

            fri=True,
            price=100
        )
        Tariff.objects.create(boat=self.boat, active=True, start_date=datetime.date(YEAR, 1, 1), end_date=datetime.date(YEAR, 12, 31),
            name='Суточно',
            duration=1,
            min=2,  

            mon=True,
            tue=True,
            wed=True,
            thu=True,
            price=5_000
        )

        self.assertEqual(_sum(21,24), 15_000)

