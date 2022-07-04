from django.test import TestCase, Client
from django.urls import reverse

from boat.tests.test_models import create_model, create_simple_boat
from boat.models import Manufacturer, Model, Boat
from user.tests.test_models import create_boat_owner, create_user

import json

class BoatTest(TestCase):
    
    def setUp(self):
        create_user('someuser@mail.ru', '12345')
        create_boat_owner('owner2@mail.ru', '12345')
        owner = create_boat_owner('owner@mail.ru', '12345')
        model = create_model()
        self.boat = create_simple_boat(model, owner)
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