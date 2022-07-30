from django.test import Client, TestCase
from django.urls import reverse
from boat.models import Boat, Tariff

from boat.tests.test_models import create_boat_owner, create_model, create_simple_boat
from user.tests.test_models import create_user
from booking.models import Booking, Prepayment

from datetime import datetime, date
import json


class BookingTestCase(TestCase):

    def setUp(self):
        self.now = datetime.now()
        self.owner = create_boat_owner('owner@mail.ru', '12345')
        self.renter = create_user('renter@mail.ru', '12345')
        self.user = create_user('user@mail.ru', '12345')

        self.boat = create_simple_boat(create_model(), self.owner, Boat.Status.PUBLISHED)
        self.booking = Booking.objects.create(boat=self.boat, renter=self.renter, start_date=date(self.now.year, 1, 1), end_date=date(self.now.year, 1, 10), total_sum=1000, spec={"test":"123"})      

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
        Tariff.objects.create(boat=self.boat, active=True, start_date=date(now.year, 1, 1), end_date=date(now.year, 12, 31),
            name='Суточно', duration=1, min=1,  
            mon=True, tue=True, wed=True, thu=True, fri=True, sat=True, sun=True, price=500
        )
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
            'end_date': date(now.year, 1, 3), 
            'total_sum': 1_000.0,
            'boat_id': self.boat.pk
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Бронирование лодки на указанный период недоступно')

        # duplicated period
        self.booking.status = Booking.Status.PENDING
        self.booking.save()
        response = _get_response({
            'start_date': date(now.year, 1, 1),
            'end_date': date(now.year, 1, 3), 
            'total_sum': 1_000.0,
            'boat_id': self.boat.pk 
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Вы уже подали бронь на указанный период')

        # ok
        response = _get_response({
            'start_date': date(now.year, 2, 1),
            'end_date': date(now.year, 2, 3), 
            'total_sum': 1_000.0,
            'boat_id': self.boat.pk 
        })
        self.assertEqual(response.status_code, 200)

    def test_set_status(self):
        booking = Booking.objects.create(boat=self.boat, renter=self.renter, start_date=date(self.now.year, 2, 1), end_date=date(self.now.year, 2, 10), total_sum=1000, spec={"test":"123"}) 
        url = reverse('booking:api_set_status', kwargs={'pk': booking.pk})
        
        # anon
        client = Client()
        response = client.post(url, {'status': Booking.Status.DECLINED})    
        self.assertRedirects(response, expected_url=reverse('user:login') + '?next=' + url)

        # owner 
        client.login(email='owner@mail.ru', password='12345')
        response = client.post(url, {'status': Booking.Status.DECLINED})
        self.assertEqual(response.status_code, 404)

        # renter
        client.login(email='renter@mail.ru', password='12345')
        
        # wrong status
        response = client.post(url, {'status': Booking.Status.ACCEPTED})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Некорректный статус')

        # ok
        response = client.post(url, {'status': Booking.Status.DECLINED})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['redirect'], reverse('booking:my_bookings'))

    def test_set_request_status(self):
        booking = Booking.objects.create(boat=self.boat, renter=self.renter, start_date=date(self.now.year, 3, 1), end_date=date(self.now.year, 3, 10), total_sum=1000, spec={"test":"123"}) 
        url = reverse('booking:api_set_request_status', kwargs={'pk': booking.pk})

        # anon
        client = Client()
        response = client.post(url, {'status': Booking.Status.DECLINED})    
        self.assertRedirects(response, expected_url=reverse('user:login') + '?next=' + url)

        # renter 
        client.login(email='renter@mail.ru', password='12345')
        response = client.post(url, {'status': Booking.Status.DECLINED})
        self.assertEqual(response.status_code, 404)

        # owner 
        client.login(email='owner@mail.ru', password='12345')

        # wrong status
        response = client.post(url, {'status': 5})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Некорректный статус')
   
        # decline no message
        response = client.post(url, {'status': Booking.Status.DECLINED})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['message'], 'Необходимо добавить сообщение')

        # decline ok
        response = client.post(url, {'status': Booking.Status.DECLINED, 'message': 'Причина отклонения'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['redirect'], reverse('booking:requests'))

        message = booking.messages.first()
        self.assertTrue((
            message.text == 'Причина отклонения' and
            message.sender == self.owner and
            message.recipient == self.renter and
            message.booking == booking
        ))

        # accept
        self.boat.prepayment_required = True
        self.boat.save()
        booking.status = Booking.Status.PENDING
        booking.save()

        response = client.post(url, {'status': Booking.Status.ACCEPTED})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['redirect'], reverse('booking:requests')) 
        self.assertTrue(booking.prepayment)
        
