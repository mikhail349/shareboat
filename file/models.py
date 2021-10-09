from django.db import models
from django.conf import settings
from django.dispatch.dispatcher import receiver

import uuid
import os

from asset.models import Asset

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

class File(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=get_file_path)

    def __str__(self):
        return self.name or ''

class AssetFile(File):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='files')
    
    def __str__(self):
        return '%s - %s' % (self.name, self.asset)

def _delete_file(path):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
    except:
        pass

@receiver(models.signals.pre_save, sender=AssetFile)
def pre_save_file(sender, instance, *args, **kwargs):
    if not instance.pk:
        instance.name = instance.file.name
    else:
        cur_file = AssetFile.objects.get(pk=instance.pk).file
        if cur_file != instance.file:
            instance.name = instance.file.name
            _delete_file(cur_file.path)

@receiver(models.signals.post_delete, sender=AssetFile)
def post_delete_file(sender, instance, *args, **kwargs):
    if instance.file:
        _delete_file(instance.file.path)

