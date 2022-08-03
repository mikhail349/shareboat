from django.core.exceptions import ValidationError
from django.db import models, transaction
from PIL import Image, UnidentifiedImageError

import logging
logger = logging.getLogger(__name__)

from . import utils

def verify_imagefile(sender, instance, *args, **kwargs):
    for field in sender._meta.fields:
        if isinstance(field, models.ImageField):
            image_file = getattr(instance, field.name)
            if image_file:
                MAX_FILE_SIZE_MB = 7
                if image_file.size > (MAX_FILE_SIZE_MB * 1024 * 1024):
                    raise ValidationError(f'Размер файла превышает {MAX_FILE_SIZE_MB} МБ')

                try:
                    img = Image.open(image_file)
                    img.verify()
                except UnidentifiedImageError:
                    raise ValidationError('Файл не явялется изображением')
                           
def compress_imagefile(sender, instance, created, *args, **kwargs):
    try: 
        for field in sender._meta.fields:
            if isinstance(field, models.ImageField):
                image_file = getattr(instance, field.name)
                if image_file:
                    img = Image.open(image_file.path)
                    img = img.resize(utils.limit_size(img.width, img.height), Image.ANTIALIAS)
                    img.save(image_file.path, format="webp") 
    except Exception as e: # pragma: no cover
        logger.error(str(e))