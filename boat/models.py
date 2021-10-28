from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from boat.validators import validate_even

from user.models import User
from file import utils, signals

class Boat(models.Model):
    name    = models.CharField(max_length=255)
    owner   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boats")

    length  = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    width   = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    draft   = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])

    def clean(self):
        pass
        #if self.length == 0:
        #    raise ValidationError({'length': _('Укажите длину лодки')})   

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Boat, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class BoatFile(models.Model):
    file = models.ImageField(upload_to=utils.get_file_path)
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return '%s - %s' % (self.file, self.boat)

pre_save.connect(signals.verify_imagefile, sender=BoatFile)
pre_save.connect(signals.delete_old_file, sender=BoatFile)
post_save.connect(signals.compress_imagefile, sender=BoatFile)
post_delete.connect(signals.delete_file, sender=BoatFile)