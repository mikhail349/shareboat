from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse

from boat.tests.test_models import create_model, create_simple_boat
from boat.models import BoatFav, Manufacturer, Model, Boat, BoatPrice
from boat.views import refresh_boat_price_period
from booking.models import Booking

from file.tests.test_models import get_imagefile
from user.tests.test_models import create_boat_owner, create_user

from django.contrib.auth.models import Group, Permission

import json
import datetime

class BoatTest(TestCase):

    def _get_post_data(self):
        return {
            'name': 'Boat2', 
            'length': 1, 
            'width': 1, 
            'draft': 1, 
            'capacity': 1, 
            'model': self.model.pk, 
            'prices': '[{"start_date": "2022-01-01", "end_date": "2022-12-31", "price": "123.45"}]',
            'file': get_imagefile(),        
            'type': Boat.Type.SAILING_YACHT,
            'motor_amount': 1,
            'motor_power': 8,
            'berth_amount': 2,
            'cabin_amount': 1,
            'bathroom_amount': 3,

            'is_custom_location': True,
            'boat_coordinates': '{"lat": 123.456789, "lon": 987.654321, "address": "Russia, Moscow", "state": "Moscow"}'
        }
    
    def setUp(self):
        self.user = create_user('someuser@mail.ru', '12345')
        create_boat_owner('owner2@mail.ru', '12345')
        self.owner = create_boat_owner('owner@mail.ru', '12345')
        self.model = create_model()
        self.boat = create_simple_boat(self.model, self.owner)
        self.client = Client()
        
    def test_get_models(self):
        manufacturer = Manufacturer.objects.create(name="Manufacturer1")
        m1 = Model.objects.create(name="Model1", manufacturer=manufacturer)
        m2 = Model.objects.create(name="Model2", manufacturer=manufacturer)

        self.client.login(email='someuser@mail.ru', password='12345')
        response = self.client.get(reverse('boat:api_get_models', kwargs={'pk': manufacturer.pk}))
        self.assertDictEqual(json.loads(response.content), {
            'data': [
                {
                    'id': m1.pk,
                    'name': 'Model1'
                    
                },
                {
                    'id': m2.pk,
                    'name': 'Model2'
                }
            ]
        })

    def test_my_boats(self):
        self.client.login(email='someuser@mail.ru', password='12345')
        response = self.client.get(reverse('boat:my_boats'))
        self.assertEqual(response.status_code, 403)

        self.client.login(email='owner@mail.ru', password='12345')
        response = self.client.get(reverse('boat:my_boats'))
        self.assertEqual(len(response.context['boats']), 1)

        self.client.login(email='owner2@mail.ru', password='12345')
        response = self.client.get(reverse('boat:my_boats'))
        self.assertEqual(len(response.context['boats']), 0)

    def test_set_status(self):
        self.client.login(email='owner2@mail.ru', password='12345')
        response = self.client.post(reverse('boat:api_set_status', kwargs={'pk': self.boat.pk}), {'status': Boat.Status.ON_MODERATION})
        self.assertEqual(response.status_code, 404)

        self.client.login(email='owner@mail.ru', password='12345')
        response = self.client.post(reverse('boat:api_set_status', kwargs={'pk': self.boat.pk}), {'status': Boat.Status.SAVED})
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(json.loads(response.content), {'message': 'Некорректный статус'})

        response = self.client.post(reverse('boat:api_set_status', kwargs={'pk': self.boat.pk}), {'status': Boat.Status.ON_MODERATION})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Boat.objects.get(pk=self.boat.pk).status, Boat.Status.ON_MODERATION)

    def test_create_boat(self):
        self.client.login(email='owner@mail.ru', password='12345')
        
        response = self.client.get(reverse('boat:create'))
        self.assertEqual(response.status_code, 200)

        data = {
            'prices': '[]',
            'model': 982,
            'file': [get_imagefile() for _ in range(11)]
        }
        
        response = self.client.post(reverse('boat:create'), data)
        self.assertEqual(response.status_code, 400)
        msg = json.loads(response.content)['message']
        self.assertEqual(msg[0], 'Модель не найдена')
        self.assertEqual(msg[1], 'Можно приложить не более 10 фотографий')

        response = self.client.post(reverse('boat:create'), self._get_post_data())
        self.assertEqual(response.status_code, 200)

        boat_pk = json.loads(response.content)['data']['id']
        boat = Boat.objects.get(pk=boat_pk)
        self.assertTrue(hasattr(boat, 'motor_boat'))
        self.assertTrue(hasattr(boat, 'comfort_boat'))
        self.assertTrue(hasattr(boat, 'coordinates'))

    def test_update_boat(self):
        self.client.login(email='owner@mail.ru', password='12345')

        response = self.client.get(reverse('boat:update', kwargs={'pk': 997}))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('boat:update', kwargs={'pk': self.boat.pk}))
        self.assertEqual(response.status_code, 200)

        self.boat.status = Boat.Status.DECLINED
        self.boat.save()
        response = self.client.post(reverse('boat:update', kwargs={'pk': self.boat.pk}), self._get_post_data())
        self.boat = Boat.objects.get(pk=self.boat.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.boat.status, Boat.Status.SAVED)

        self.boat.status = Boat.Status.PUBLISHED
        self.boat.save()
        response = self.client.post(reverse('boat:update', kwargs={'pk': self.boat.pk}), self._get_post_data())
        self.boat = Boat.objects.get(pk=self.boat.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.boat.status, Boat.Status.ON_MODERATION)

        data = {
            **self._get_post_data(),
            'type': Boat.Type.BOAT,
            'is_custom_location': False
        }
        response = self.client.post(reverse('boat:update', kwargs={'pk': self.boat.pk}), data)
        self.boat = Boat.objects.get(pk=self.boat.pk)
        self.assertFalse(hasattr(self.boat, 'motor_boat'))
        self.assertFalse(hasattr(self.boat, 'comfort_boat'))
        self.assertFalse(hasattr(self.boat, 'coordinates'))

        response = self.client.post(reverse('boat:update', kwargs={'pk': 956}), self._get_post_data())
        self.assertTrue(response.status_code, 404)

    def test_favs(self):

        Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1, model=self.model, type=Boat.Type.BOAT, owner=self.owner, status = Boat.Status.PUBLISHED)
        boat2 = Boat.objects.create(name='Boat2', length=1, width=1, draft=1, capacity=1, model=self.model, type=Boat.Type.BOAT, owner=self.owner, status = Boat.Status.PUBLISHED)
        BoatFav.objects.create(boat=boat2, user=self.user)

        self.client.login(email='someuser@mail.ru', password='12345')
        response = self.client.get(reverse('boat:favs'))
        self.assertEqual(response.status_code, 200)

        boats = response.context['boats']
        self.assertTrue(len(boats) == 1 and boats[0].pk == boat2.pk)

    def test_boats_on_moderation(self):
        boat = create_simple_boat(self.model, self.owner)
        moderator = create_user('moderator@mail.com', '12345')
        self.client.login(email='moderator@mail.com', password='12345')

        response = self.client.get(reverse('boat:boats_on_moderation'))
        self.assertEqual(response.status_code, 403)

        moderator.groups.add(Group.objects.get(name='boat_moderator'))
        response = self.client.get(reverse('boat:boats_on_moderation'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['boats']), 0)

        boat.status = Boat.Status.ON_MODERATION
        boat.save()
        response = self.client.get(reverse('boat:boats_on_moderation'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['boats']), 1)



    def test_moderate(self):
        boat = Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1, model=self.model, type=Boat.Type.BOAT, owner=self.owner, status = Boat.Status.ON_MODERATION)
        moderator = create_user('moderator@mail.com', '12345')
        
        self.client.login(email='moderator@mail.com', password='12345')
        response = self.client.get(reverse('boat:moderate', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 403)

        moderator.groups.add(Group.objects.get(name='boat_moderator'))

        response = self.client.get(reverse('boat:moderate', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('boat:moderate', kwargs={'pk': 986}))
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        now = datetime.datetime.now()
        user = create_user('user@mail.com', '12345')
        boat = create_simple_boat(self.model, self.owner)
        booking = Booking.objects.create(
            boat=boat, 
            renter=user, 
            status=Booking.Status.ACCEPTED, 
            start_date=datetime.date(now.year, 1, 1), 
            end_date=datetime.date(now.year, 1, 10),
            total_sum=100.50
        )
        self.client.login(email='user@mail.com', password='12345')

        response = self.client.post(reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 403)

        user.groups.add(Group.objects.get(name='boat_owner'))

        response = self.client.post(reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 404)

        self.client.login(email='owner@mail.ru', password='12345')
        response = self.client.post(reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['code'], 'invalid_status')

        booking.status = Booking.Status.DONE
        booking.save()
        response = self.client.post(reverse('boat:api_delete', kwargs={'pk': boat.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Boat.objects.get(pk=boat.pk).status, Boat.Status.DELETED)


    def test_refresh_boat_price_period(self):
        now = datetime.datetime.now()
        BoatPrice.objects.create(boat=self.boat, start_date=datetime.date(now.year, 1, 1), end_date=datetime.date(now.year, 1, 10), price=100)
        BoatPrice.objects.create(boat=self.boat, start_date=datetime.date(now.year, 1, 11), end_date=datetime.date(now.year, 1, 20), price=200)
        BoatPrice.objects.create(boat=self.boat, start_date=datetime.date(now.year, 1, 25), end_date=datetime.date(now.year, 1, 30), price=300)

        refresh_boat_price_period(self.boat)
        price_periods = self.boat.prices_period.all()

        self.assertEqual(price_periods.count(), 2)
        res = (
            price_periods[0].start_date == datetime.date(now.year, 1, 1) and price_periods[0].end_date == datetime.date(now.year, 1, 20) and
            price_periods[1].start_date == datetime.date(now.year, 1, 25) and price_periods[1].end_date == datetime.date(now.year, 1, 30)
        )
        self.assertTrue(res)