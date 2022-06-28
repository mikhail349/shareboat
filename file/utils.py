from django.conf import settings

import uuid
import os

import logging
logger = logging.getLogger(__name__)

def get_file_path(instance, filename, path=""):
    #ext = filename.split('.')[-1]
    ext = 'webp'
    return "%s%s.%s" % (path, uuid.uuid4(), ext)

def remove_file(path):
    try:   
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
    except Exception as e:
        logger.error(str(e))

def limit_size(width, height, max_width = 1920, max_height = 1080):
    while width > max_width or height > max_height:
        if width > max_width:
            height = round(max_width / width * height)
            width = max_width           
        if height > max_height:
            width = round(max_height / height * width)
            height = max_height

    return (width, height)

