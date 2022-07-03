from io import BytesIO
from PIL import Image
from django.test import TestCase

from boat.models import Manufacturer, Model, Boat, BoatFile
from boat.serializers import BoatFileSerializer
from user.tests.test_models import create_boat_owner
from django.core.files.base import File


class BoatFileSerializerTest(TestCase):
  
    
    def test_filename(self):
        owner = create_boat_owner('admin@admin.ru', '12345')
        manufacturer = Manufacturer .objects.create(name="Manufacturer1")
        model = Model.objects.create(name="Model1", manufacturer=manufacturer)
        boat = Boat.objects.create(name='Boat1', length=1, width=1, draft=1, capacity=1, model=model, type=Boat.Type.BOAT, owner=owner)  

        image_file = BytesIO()
        image = Image.new('RGBA', size=(50,50), color=(256,0,0))
        image.save(image_file, 'PNG')
        image_file.seek(0)
        file = File(image_file, name='test.png')

        boat_file = BoatFile.objects.create(file=file, boat=boat)
        serializer = BoatFileSerializer(boat_file)
        print(serializer.data)
    