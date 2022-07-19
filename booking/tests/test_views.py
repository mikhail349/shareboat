from django.test import TestCase
from django.urls import reverse
from boat.models import Boat, BoatPrice

from boat.tests.test_models import create_boat_owner, create_model, create_simple_boat
from user.tests.test_models import create_user
from booking.models import Booking

from datetime import datetime, date
import json


class BookingTestCase(TestCase):

    def setUp(self):
        now = datetime.now()
        self.owner = create_boat_owner('owner@mail.ru', '12345')
        self.renter = create_user('renter@mail.ru', '12345')
        self.user = create_user('user@mail.ru', '12345')

        self.boat = create_simple_boat(create_model(), self.owner, Boat.Status.PUBLISHED)
        self.booking = Booking.objects.create(boat=self.boat, renter=self.renter, start_date=date(now.year, 1, 1), end_date=date(now.year, 1, 10), total_sum=1000)      

    def test_view(self):
        def _get_response():
            return self.client.get(reverse('booking:view', kwargs={'pk': self.booking.pk}))   

        # anon
        response = _get_response()
        self.assertEqual(response.status_code, 302)

        # foreign user
        self.client.login(email='user@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 404)

        # renter
        self.client.login(email='renter@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['booking'], self.booking)

        # owner
        self.client.login(email='owner@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['booking'], self.booking)

    def test_my_bookings(self):
        def _get_response(status=None):
            return self.client.get(reverse('booking:my_bookings'), {'status': status or ''})    

        # anon
        response = _get_response()
        self.assertEqual(response.status_code, 302)

        # owner
        self.client.login(email='owner@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['bookings']), [])

        # renter
        self.client.login(email='renter@mail.ru', password='12345')
        
        response = _get_response('')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['bookings']), [self.booking])

        response = _get_response('pending')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['bookings']), [self.booking])

        self.booking.status = Booking.Status.DONE
        self.booking.save()
        response = _get_response('done')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['bookings']), [self.booking])

        self.booking.status = Booking.Status.ACTIVE
        self.booking.save()
        response = _get_response('active')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['bookings']), [self.booking])

        self.booking.status = Booking.Status.PREPAYMENT_REQUIRED
        self.booking.save()
        response = _get_response('done')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['bookings']), [])

    def test_requests(self):
        def _get_response(status=None):
            return self.client.get(reverse('booking:requests'), {'status': status or ''})    

        # anon
        response = _get_response()
        self.assertEqual(response.status_code, 302)

        # renter
        self.client.login(email='renter@mail.ru', password='12345')
        response = _get_response()
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['requests']), [])

        # owner
        self.client.login(email='owner@mail.ru', password='12345')
        
        response = _get_response('')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['requests']), [self.booking])

        response = _get_response('pending')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['requests']), [self.booking])

        self.booking.status = Booking.Status.DONE
        self.booking.save()
        response = _get_response('done')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['requests']), [self.booking])

        self.booking.status = Booking.Status.ACTIVE
        self.booking.save()
        response = _get_response('active')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['requests']), [self.booking])

        self.booking.status = Booking.Status.PREPAYMENT_REQUIRED
        self.booking.save()
        response = _get_response('done')
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(list(response.context['requests']), [])

    def test_create(self):
        def _get_response(data):
            return self.client.post(reverse('booking:api_create'), data)    

        now = datetime.now()

        # anon
        response = _get_response({
            'start_date': date(now.year, 1, 5),
            'end_date': date(now.year, 1, 6), 
            'total_sum': 200.0,
            'boat_id': self.boat.pk 
        })
        self.assertEqual(response.status_code, 302)       

        # login as renter
        self.client.login(email='renter@mail.ru', password='12345')

        # not found
        response = _get_response({
            'start_date': date(now.year, 2, 5),
            'end_date': date(now.year, 2, 6), 
            'total_sum': 200.0,
            'boat_id': 999 
        })
        self.assertEqual(response.status_code, 404) 

        # wrong price
        BoatPrice.objects.create(boat=self.boat, start_date=date(now.year, 1, 1), end_date=date(now.year, 12, 31), price=200)
        response = _get_response({
            'start_date': date(now.year, 2, 5),
            'end_date': date(now.year, 2, 6), 
            'total_sum': 200.0,
            'boat_id': self.boat.pk 
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['code'], 'outdated_price')

        # wrong period
        self.booking.status = Booking.Status.ACCEPTED
        self.booking.save()
        response = _get_response({
            'start_date': date(now.year, 1, 1),
            'end_date': date(now.year, 1, 2), 
            'total_sum': 400.0,
            'boat_id': self.boat.pk 
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Бронирование лодки на указанный период недоступно')

        # duplicated period
        self.booking.status = Booking.Status.PENDING
        self.booking.save()
        response = _get_response({
            'start_date': date(now.year, 1, 1),
            'end_date': date(now.year, 1, 2), 
            'total_sum': 400.0,
            'boat_id': self.boat.pk 
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Вы уже подали бронь на указанный период')

        # ok
        response = _get_response({
            'start_date': date(now.year, 2, 1),
            'end_date': date(now.year, 2, 2), 
            'total_sum': 400.0,
            'boat_id': self.boat.pk 
        })
        self.assertEqual(response.status_code, 200)