from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from boat.models import Boat, BoatFav, Manufacturer, Model
from user.tests.test_models import create_boat_owner
   

class BoatTest(TestCase):

    def create_model(self):
        manufacturer = Manufacturer.objects.create(name="Manufacturer1")
        return Model.objects.create(name="Model1", manufacturer=manufacturer)

    def create_simple_boat(self, owner):
        return Boat.objects.create(name='Лодка1', length=1, width=1, draft=1, capacity=1, model=self.model, type=Boat.Type.BOAT, owner=owner)   

    def setUp(self):
        self.owner = create_boat_owner('admin@admin.ru', '12345')
        self.model = self.create_model()
        self.boat = self.create_simple_boat(self.owner)

    def test_active_boat_manager(self):
        boats = Boat.active.all()
        self.assertEqual(len(boats), 1)
        
        self.boat.status = Boat.Status.DELETED
        self.boat.save()

        boats = Boat.active.all()
        self.assertEqual(len(boats), 0)

    def test_published_boat_manager(self):
        boats = Boat.published.all()
        self.assertEqual(len(boats), 0)

        self.boat.status = Boat.Status.PUBLISHED
        self.boat.save()

        boats = Boat.published.all()
        self.assertEqual(len(boats), 1)

    def test_annotate_in_fav(self):
        anonym = AnonymousUser()
        
        self.boat.status = Boat.Status.PUBLISHED
        self.boat.save()
        boats = Boat.published.all().annotate_in_fav(user=anonym)
        self.assertFalse(boats[0].in_fav)

        BoatFav.objects.create(boat=self.boat, user=self.owner)
        boats = Boat.published.all().annotate_in_fav(user=self.owner)
        self.assertTrue(boats[0].in_fav)

    def test_is_published(self):
        self.assertFalse(self.boat.is_published)
        self.boat.status = Boat.Status.PUBLISHED
        self.boat.save()
        self.assertTrue(self.boat.is_published)

class ManufacturerModelTest(TestCase):

    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(name="Manufacturer1")
        self.model = Model.objects.create(name="Model1", manufacturer=self.manufacturer)

    def test_manufacturer_creation(self):
        self.assertEqual(str(self.manufacturer), 'Manufacturer1')

    def test_model_creation(self):
        self.assertEqual(str(self.model), 'Model1')
