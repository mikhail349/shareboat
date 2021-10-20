from django.db import models, transaction
from django.dispatch.dispatcher import receiver
from PIL import Image

from asset.models import Asset
from . import utils

class AssetFile(models.Model):
    file = models.ImageField(upload_to=utils.get_file_path)
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
            transaction.on_commit(lambda: utils.remove_file(cur_file.path))


@receiver(models.signals.post_save, sender=AssetFile)
def compress_imagefile(sender, instance, created, *args, **kwargs):
    img = Image.open(instance.file.path)
    img = img.resize(utils.limit_size(img.width, img.height), Image.ANTIALIAS)
    img.save(instance.file.path, quality=70, optimize=True)        


@receiver(models.signals.post_delete, sender=AssetFile)
def post_delete_asset_file(sender, instance, *args, **kwargs):
    if instance.file:
        transaction.on_commit(lambda: utils.remove_file(instance.file.path))
