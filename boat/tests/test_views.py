from django.test import TestCase, Client
from django.urls import reverse

from boat.tests.test_models import create_model, create_simple_boat
from boat.models import Manufacturer, Model
from user.tests.test_models import create_boat_owner

import json

class BoatTest(TestCase):
    
    def setUp(self):
        create_boat_owner('admin@admin.ru', '12345')
        self.client = Client()
        self.client.login(email='admin@admin.ru', password='12345')

    def test_get_models(self):
        manufacturer = Manufacturer.objects.create(name="Manufacturer1")
        m1 = Model.objects.create(name="Model1", manufacturer=manufacturer)
        m2 = Model.objects.create(name="Model2", manufacturer=manufacturer)

        response = self.client.get(reverse('boat:api_get_models', kwargs={'pk': manufacturer.pk}))
        self.assertDictEqual(json.loads(response.content), {
            'data': [
                {
                    'id': m1.pk,
                    'name': m1.name
                    
                },
                {
                    'id': m2.pk,
                    'name': m2.name
                }
            ]
        })
