from django.db import models, transaction
from PIL import Image, UnidentifiedImageError

import logging

from django.forms import ValidationError
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

def delete_old_file(sender, instance, *args, **kwargs):
    if instance.pk:    
        cur_instance = sender.objects.get(pk=instance.pk)
        for field in sender._meta.fields:
            if isinstance(field, models.FileField):
                cur_file = getattr(cur_instance, field.name) 
                if cur_file:
                    if cur_file != getattr(instance, field.name):                      
                        transaction.on_commit(lambda: utils.remove_file(cur_file.path))  

                                  
def compress_imagefile(sender, instance, created, *args, **kwargs):
    try: 
        for field in sender._meta.fields:
            if isinstance(field, models.ImageField):
                image_file = getattr(instance, field.name)
                if image_file:
                    img = Image.open(image_file.path)
                    img = img.resize(utils.limit_size(img.width, img.height), Image.ANTIALIAS)
                    img.save(image_file.path, quality=70, optimize=True) 
    except Exception as e:
        logger.error(str(e))


def delete_file(sender, instance, *args, **kwargs):
    def f():
        for field in sender._meta.fields:
            if isinstance(field, models.FileField):
                image_file = getattr(instance, field.name)
                if image_file:
                    utils.remove_file(image_file.path)
    transaction.on_commit(f)

    
