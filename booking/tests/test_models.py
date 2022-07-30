from django.test import TestCase

from boat.tests.test_models import create_boat_owner, create_model, create_simple_boat
from booking.exceptions import BookingDateRangeException, BookingDuplicatePendingException
from booking.models import Booking

from datetime import date, datetime

class BookingTest(TestCase):
    
    def test_booking_creation(self):
        owner = create_boat_owner('owner@mail.ru', '12345')
        model = create_model()
        boat = create_simple_boat(model, owner)

        now = datetime.now()
        booking = Booking.objects.create(boat=boat, renter=owner, start_date=date(now.year, 1, 1), end_date=date(now.year, 1, 10), total_sum=1000, spec={"test":"123"})
        self.assertEqual(str(booking), 'Бронь № %s - Boat1 (Лодка)' % booking.pk) 

        with self.assertRaises(BookingDateRangeException):
            booking.status = Booking.Status.ACCEPTED
            booking.save()
            Booking.objects.create(boat=boat, renter=owner, start_date=date(now.year, 1, 2), end_date=date(now.year, 1, 3), total_sum=200, spec={"test":"123"})

        with self.assertRaises(BookingDuplicatePendingException):
            booking.status = Booking.Status.PENDING
            booking.save()
            Booking.objects.create(boat=boat, renter=owner, start_date=date(now.year, 1, 2), end_date=date(now.year, 1, 3), total_sum=200, spec={"test":"123"})