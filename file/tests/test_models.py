from io import BytesIO
from django.core.files.base import File
from PIL import Image

def get_imagefile():
    image_file = BytesIO()
    image = Image.new('RGBA', size=(50,50), color=(256,0,0))
    image.save(image_file, 'PNG')
    image_file.seek(0)
    return File(image_file, name='test.png')