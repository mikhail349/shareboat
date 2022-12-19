from tkinter import image_types
from django.test import TestCase

from booking.models import Booking 
from booking.templatetags.booking_extras import get_status_color, spectolist
from boat.tests.test_models import create_boat_owner, create_model, create_simple_boat

from datetime import datetime, date
from decimal import Decimal

class TestCase(TestCase):
    def test_get_status_color(self):
        self.assertEqual(get_status_color(Booking.Status.DECLINED), 'bg-booking-data text-danger')
        self.assertEqual(get_status_color(Booking.Status.ACCEPTED), 'bg-light text-success')
        self.assertEqual(get_status_color(Booking.Status.ACTIVE), 'bg-light text-secondary')
        self.assertEqual(get_status_color(Booking.Status.DONE), 'bg-light text-secondary')

    def test_spectolist(self):
        owner = create_boat_owner('owner@mail.ru', '12345')
        model = create_model()
        boat = create_simple_boat(model, owner)
        now = datetime.now()

        spec='{"1": {"name": "Неделя", "price": "130.50", "amount": "2", "sum": "261.00"}}'
        booking = Booking.objects.create(boat=boat, renter=owner, start_date=date(now.year, 1, 2), end_date=date(now.year, 1, 3), total_sum=200, spec=spec)

        l = spectolist(booking.spec)
        self.assertEqual(l[0]['price'], Decimal("130.50"))
        self.assertEqual(l[0]['sum'], Decimal("261.00"))

        booking = Booking.objects.create(boat=boat, renter=owner, start_date=date(now.year, 2, 2), end_date=date(now.year, 2, 3), total_sum=200, spec="abcd")
        self.assertListEqual(spectolist(booking.spec), [])
