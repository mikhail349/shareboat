from typing import Type
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
#from boat.validators import validate_even

from user.models import User
from file import utils, signals

class Boat(models.Model):

    class Type(models.IntegerChoices):
        SAILING_YACHT   = 0, _("Парусная яхта")
        MOTOR_BOAT      = 1, _("Катер/моторная лодка")
        BOAT            = 2, _("Лодка")
        GULET           = 3, _("Гулет")
        JET_SKI         = 4, _("Гидроцикл")
        MOTOR_YACHT     = 5, _("Моторная яхта")
        HOUSE_BOAT      = 6, _("Хаусбот")
        CATAMARAN       = 7, _("Катамаран")
        TRIMARAN        = 8, _("Тримаран")

    name    = models.CharField(max_length=255)
    owner   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boats")

    length  = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    width   = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    draft   = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    capacity = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)])

    type    = models.IntegerField(choices=Type.choices)

    def clean(self):
        pass
        #if self.length == 0:
        #    raise ValidationError({'length': _('Укажите длину лодки')})   

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Boat, self).save(*args, **kwargs)

    def is_motor_boat(self):
        return self.type in self.get_motor_boat_types()

    def is_comfort_boat(self):
        return self.type in self.get_comfort_boat_types()

    @classmethod
    def get_motor_boat_types(cls):
        return [cls.Type.SAILING_YACHT, cls.Type.MOTOR_BOAT, cls.Type.GULET, cls.Type.JET_SKI, cls.Type.MOTOR_YACHT, cls.Type.HOUSE_BOAT, cls.Type.CATAMARAN, cls.Type.TRIMARAN]

    @classmethod
    def get_comfort_boat_types(cls):
        return [cls.Type.SAILING_YACHT, cls.Type.GULET, cls.Type.MOTOR_YACHT, cls.Type.HOUSE_BOAT, cls.Type.CATAMARAN, cls.Type.TRIMARAN]

    @classmethod
    def get_types(cls):
        types = cls.Type.choices
        return sorted(types, key=lambda tup: tup[1])
    
    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())

class MotorBoat(models.Model):
    boat = models.OneToOneField(Boat, on_delete=models.CASCADE, primary_key=True, related_name="motor_boat")
    motor_amount    = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    motor_power     = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2000)])

class ComfortBoat(models.Model):
    boat = models.OneToOneField(Boat, on_delete=models.CASCADE, primary_key=True, related_name="comfort_boat")
    berth_amount    = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    cabin_amount    = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    bathroom_amount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])

class Specification(models.Model):
    
    class Category(models.IntegerChoices):
        OTHER       = 0, _("Прочее")
        ELECTRONICS = 1, _("Электроника")

    name        = models.CharField(max_length=255)
    #amount      = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(999)])
    boat        = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name="specifications")
    сategory    = models.IntegerField(choices=Category.choices)

    @classmethod
    def get_сategories(cls):
        сategories = cls.Category.choices
        return sorted(сategories, key=lambda tup: tup[1])

class BoatFile(models.Model):
    file = models.ImageField(upload_to=utils.get_file_path)
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return '%s - %s' % (self.file, self.boat)

pre_save.connect(signals.verify_imagefile, sender=BoatFile)
pre_save.connect(signals.delete_old_file, sender=BoatFile)
post_save.connect(signals.compress_imagefile, sender=BoatFile)
post_delete.connect(signals.delete_file, sender=BoatFile)