from django.test import TestCase
from django.contrib.auth.models import AnonymousUser

from boat.models import Boat, BoatFav, BoatCoordinates, Manufacturer, Model, Specification, get_upload_to
from user.tests.test_models import create_boat_owner

import datetime
   

def create_model():
    manufacturer = Manufacturer.objects.create(name="Manufacturer1")
    return Model.objects.create(name="Model1", manufacturer=manufacturer)

def create_simple_boat(model, owner, status=Boat.Status.SAVED):
    return Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1, model=model, type=Boat.Type.BOAT, owner=owner, status=status)  


class BoatTest(TestCase):

    def setUp(self):
        self.owner = create_boat_owner('admin@admin.ru', '12345')
        self.model = create_model()
        self.boat = create_simple_boat(self.model, self.owner)

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

    def test_published(self):
        self.assertFalse(self.boat.is_published)
        self.boat.status = Boat.Status.PUBLISHED
        self.boat.save()
        self.assertTrue(self.boat.is_published)

    def test_full_name(self):
        self.assertEqual(self.boat.get_full_name(), 'Manufacturer1 Model1 "Boat1"')

    def test_clean(self):
        boat = Boat(name='Boat1', text=" ", issue_year="", length=1, width=1, draft=1, capacity=1, model=self.model, type=Boat.Type.BOAT, owner=self.owner)   
        boat.clean()
        self.assertIsNone(boat.text)
        self.assertIsNone(boat.issue_year)

    def test_is_motor_boat(self):
        self.assertFalse(self.boat.is_motor_boat())
        self.boat.type = Boat.Type.HOUSE_BOAT
        self.boat.save()
        self.assertTrue(self.boat.is_motor_boat())

    def test_is_comfort_boat(self):
        self.assertFalse(self.boat.is_comfort_boat())
        self.boat.type = Boat.Type.MOTOR_YACHT
        self.boat.save()
        self.assertTrue(self.boat.is_comfort_boat())

    def test_is_custom_location(self):
        self.assertFalse(self.boat.is_custom_location())
        BoatCoordinates.objects.create(boat=self.boat, lon=123.456789, lat=987.654321, address="Moscow, 15", state="Moscow")
        self.assertTrue(self.boat.is_custom_location())

    def test_get_types(self):
        boat_types = Boat.get_types()
        self.assertEqual(len(boat_types), len(Boat.Type.choices))
        self.assertListEqual(boat_types, sorted(boat_types, key=lambda item: item[1]))

    def test_repr(self):
        self.assertTrue(str(self.boat), 'Boat1 Лодка')

class BoatFileTest(TestCase):
    def test_get_upload_to(self):
        res = get_upload_to(None, None)
        self.assertTrue(res.startswith('boat/'))
        self.assertTrue(res.endswith('.webp'))

class ManufacturerModelTest(TestCase):

    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(name="Manufacturer1")
        self.model = Model.objects.create(name="Model1", manufacturer=self.manufacturer)

    def test_manufacturer_creation(self):
        self.assertEqual(str(self.manufacturer), 'Manufacturer1')

    def test_model_creation(self):
        self.assertEqual(str(self.model), 'Model1')

class SpecificationTest(TestCase):

    def test_get_сategories(self):
        categories = Specification.get_сategories()
        self.assertEqual(len(categories), len(Specification.Category.choices))
        self.assertListEqual(categories, sorted(categories, key=lambda item: item[1]))
