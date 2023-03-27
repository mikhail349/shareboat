from django.test import TestCase

from base.models import Base


class BaseTest(TestCase):
    
    def test_base_creation(self):
        base = Base.objects.create(name='Base1', lon=123.456789, lat=987.654321, address="Moscow, 15", state="Moscow")
        self.assertEqual(str(base), 'Base1 (Moscow)')