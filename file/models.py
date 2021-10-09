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
    filename = models.CharField(max_length=255, null=True, blank=True)
    data = models.FileField(upload_to=get_file_path)

    def __str__(self):
        return self.filename

class AssetFile(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE, primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return '%s - %s' % (self.file, self.asset)

def _delete_file(path):
    try:
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
    except:
        pass

@receiver(models.signals.pre_save, sender=File)
def pre_save_file(sender, instance, *args, **kwargs):
    if not instance.pk:
        instance.filename = instance.data.name
    else:
        cur_file_data = File.objects.get(pk=instance.pk).data
        if cur_file_data != instance.data:
            instance.filename = instance.data.name
            _delete_file(cur_file_data.path)

@receiver(models.signals.post_delete, sender=File)
def post_delete_file(sender, instance, *args, **kwargs):
    if instance.data:
        _delete_file(instance.data.path)

