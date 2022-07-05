from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse

from boat.tests.test_models import create_model, create_simple_boat
from boat.models import Manufacturer, Model, Boat
from file.tests.test_models import get_imagefile
from user.tests.test_models import create_boat_owner, create_user

import json

class BoatTest(TestCase):

    def _get_post_data(self):
        return {
            'name': 'Boat2', 
            'length': 1, 
            'width': 1, 
            'draft': 1, 
            'capacity': 1, 
            'model': self.model.pk, 
            'type': Boat.Type.BOAT,
            'prices': '[{"start_date": "2022-01-01", "end_date": "2022-12-31", "price": "123.45"}]',
            'file': get_imagefile()
        }
    
    def setUp(self):
        create_user('someuser@mail.ru', '12345')
        create_boat_owner('owner2@mail.ru', '12345')
        owner = create_boat_owner('owner@mail.ru', '12345')
        self.model = create_model()
        self.boat = create_simple_boat(self.model, owner)
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

    def test_update_boat(self):
        self.client.login(email='owner@mail.ru', password='12345')

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