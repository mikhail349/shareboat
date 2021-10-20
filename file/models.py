from django.db import models
from django.conf import settings
from django.dispatch.dispatcher import receiver
from PIL import Image

import uuid
import os
import math

from asset.models import Asset

def get_file_path(instance, filename):
    #instance._meta.model.__name__, 
    ext = filename.split('.')[-1]
    return "%s.%s" % (uuid.uuid4(), ext)

def remove_file(path):
    pass
    '''
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
    except:
        pass
    '''


class AssetFile(models.Model):
    file = models.ImageField(upload_to=get_file_path)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return '%s - %s' % (self.file, self.asset)


@receiver(models.signals.pre_save, sender=AssetFile)
def pre_save_asset_file(sender, instance, *args, **kwargs):
    img = Image.open(instance.file)
    img.verify()
    if instance.pk:
        cur_file = AssetFile.objects.get(pk=instance.pk).file
        if cur_file != instance.file:
            remove_file(cur_file.path)


@receiver(models.signals.post_save, sender=AssetFile)
def compress_imagefile(sender, instance, created, *args, **kwargs):
    img = Image.open(instance.file.path)

    width, height = img.size 
    max_width = 1920
    max_height = 1080

    while width > max_width or height > max_height:
        if width > max_width:
            height = round(max_width / width * height)
            width = max_width           
        if height > max_height:
            width = round(max_height / height * width)
            height = max_height

    img = img.resize((width, height), Image.ANTIALIAS)
    img.save(instance.file.path, quality=70, optimize=True)        


@receiver(models.signals.post_delete, sender=AssetFile)
def post_delete_asset_file(sender, instance, *args, **kwargs):
    if instance.file:
        remove_file(instance.file.path)
