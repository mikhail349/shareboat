from django.test import TestCase
from boat.exceptions import PriceDateRangeException

class PriceDateRangeExceptionTest(TestCase):
    
    def test_creation(self):
        e = PriceDateRangeException()
        self.assertEqual(str(e), 'Выбранный период содержит недоступные даты')