from django.test import TestCase

from booking.models import Booking 
from booking.templatetags.booking_extras import get_status_color

class BookingExtrasTestCase(TestCase):
    def test_get_status_color(self):
        self.assertEqual(get_status_color(Booking.Status.DECLINED), 'bg-light text-danger')
        self.assertEqual(get_status_color(Booking.Status.ACCEPTED), 'bg-light text-success')
        self.assertEqual(get_status_color(Booking.Status.ACTIVE), 'bg-light text-secondary')
        self.assertEqual(get_status_color(Booking.Status.DONE), 'bg-light text-secondary')
