from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from PIL import Image

from asset.models import Asset
from . import utils, signals

MAX_FILE_SIZE = 5 * 1024 * 1024

class AssetFile(models.Model):
    file = models.ImageField(upload_to=utils.get_file_path)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return '%s - %s' % (self.file, self.asset)

pre_save.connect(signals.verify_imagefile, sender=AssetFile)
pre_save.connect(signals.delete_changing_file, sender=AssetFile)
post_save.connect(signals.compress_imagefile, sender=AssetFile)
post_delete.connect(signals.delete_file, sender=AssetFile)