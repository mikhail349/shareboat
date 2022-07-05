import os
from django.test import TestCase

from boat.models import Manufacturer, Model, Boat, BoatFile
from boat.serializers import BoatFileSerializer
from file.tests.test_models import get_imagefile
from user.tests.test_models import create_boat_owner


class BoatFileSerializerTest(TestCase):
  
    def test_filename(self):
        owner = create_boat_owner('admin@admin.ru', '12345')
        manufacturer = Manufacturer .objects.create(name="Manufacturer1")
        model = Model.objects.create(name="Model1", manufacturer=manufacturer)
        boat = Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1, model=model, type=Boat.Type.BOAT, owner=owner)  

        file = get_imagefile()
        boat_file = BoatFile.objects.create(file=file, boat=boat)
        serializer = BoatFileSerializer(boat_file)
        self.assertEqual(serializer.data.get('filename'), os.path.basename(boat_file.file.name))
    