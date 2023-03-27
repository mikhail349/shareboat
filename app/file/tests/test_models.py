from io import BytesIO

from django.core.files.base import File
from PIL import Image


def get_imagefile(filename='test.png', size=(50,50)):
    image_file = BytesIO()
    image = Image.new('RGBA', size=size, color=(256,0,0))
    image.save(image_file, 'PNG')
    image_file.seek(0)
    return File(image_file, name=filename)

def get_file(filename='file.txt'):
    file = BytesIO(b'Inital value for read buffer')
    file.seek(0)
    return File(file, name=filename)