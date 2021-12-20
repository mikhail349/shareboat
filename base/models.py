from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_save, post_delete

from file import utils, signals

class Base(models.Model):
    name    = models.CharField(max_length=255)
    lon     = models.DecimalField(max_digits=9, decimal_places=6)
    lat     = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    
    website = models.URLField(max_length=255, null=True, blank=True)
    phone   = models.CharField(
        max_length=10, 
        null=True, 
        blank=True, 
        validators=[
            RegexValidator(
                regex=r'(\d+){10}',
                message=_("Номер телефона должен содержать 10 цифр"),
                code="invalid_phone"
            )
        ]
    )

    def __str__(self):
        return self.name

class BaseImage(models.Model):
    image = models.ImageField(upload_to=utils.get_file_path)
    base = models.ForeignKey(Base, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return '%s - %s' % (self.image, self.base)

pre_save.connect(signals.verify_imagefile, sender=BaseImage)
pre_save.connect(signals.delete_old_file, sender=BaseImage)
post_save.connect(signals.compress_imagefile, sender=BaseImage)
post_delete.connect(signals.delete_file, sender=BaseImage)