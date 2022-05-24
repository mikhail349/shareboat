from pyexpat import model
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, post_delete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from shareboat.utils import has_swear

from user.models import User
from file import utils, signals
from base.models import Base

class ActiveBoatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status=Boat.Status.DELETED)

class PublishedBoatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Boat.Status.PUBLISHED)

class Manufacturer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Model(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name="models")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Boat(models.Model):

    class Meta:
        permissions = [
            ('can_view_boats_on_moderation', 'Can view boats on moderation'),
            ('can_moderate_boats', 'Can moderate boats'),
        ]

    class Status(models.IntegerChoices):
        DELETED         = -2, _("Удалена")
        DECLINED        = -1, _("Отклонена")
        SAVED           = 0, _("Сохранена")
        ON_MODERATION   = 1, _("На проверке")  
        PUBLISHED       = 2, _("Опубликована")

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

    name    = models.CharField(max_length=255, null=True, blank=True)
    text    = models.TextField(null=True, blank=True)
    owner   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boats")
    model   = models.ForeignKey(Model, on_delete=models.PROTECT, related_name="boats", null=True, blank=True)
    status  = models.IntegerField(choices=Status.choices, default=Status.SAVED)

    issue_year = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1900), MaxValueValidator(2999)])
    length  = models.DecimalField(max_digits=4, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    width   = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    draft   = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])
    capacity = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)])
    type    = models.IntegerField(choices=Type.choices)
    prepayment_required = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)

    base    = models.ForeignKey(Base, on_delete=models.PROTECT, related_name="boats", null=True, blank=True)

    objects = models.Manager()
    active = ActiveBoatManager()
    published = PublishedBoatManager()

    @property
    def is_draft(self):
        return self.status == self.Status.SAVED

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    def get_now_prices(self):
        now = timezone.now()
        return BoatPrice.objects.filter(boat=self, start_date__lte=now, end_date__gte=now)

    def get_future_prices(self):
        now = timezone.now()
        return BoatPrice.objects.filter(boat=self, start_date__gt=now)

    def clean(self):
        if self.text:
            self.text = self.text.strip()
        if self.text == "":
            self.text = None
        if self.issue_year == "":
            self.issue_year = None 

        '''
        errors = []
        if has_swear(self.name):
            errors.append(ValidationError("Похоже, название лодки содержит нецензурное слово", code="swear"))

        if has_swear(self.text):
            errors.append(ValidationError("Похоже, описание лодки содержит нецензурное слово", code="swear"))

        if errors:
            raise ValidationError(errors)
        '''

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Boat, self).save(*args, **kwargs)

    def is_motor_boat(self):
        return self.type in self.get_motor_boat_types()

    def is_comfort_boat(self):
        return self.type in self.get_comfort_boat_types()

    def is_custom_location(self):
        try:
            r = self.coordinates
            return True
        except BoatCoordinates.DoesNotExist:
            return False

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
    motor_power     = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(Decimal('0.1'))])

class ComfortBoat(models.Model):
    boat = models.OneToOneField(Boat, on_delete=models.CASCADE, primary_key=True, related_name="comfort_boat")
    berth_amount    = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    cabin_amount    = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    bathroom_amount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])

class BoatCoordinates(models.Model):
    boat = models.OneToOneField(Boat, on_delete=models.CASCADE, primary_key=True, related_name="coordinates")
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    state = models.CharField(max_length=255)

class Specification(models.Model):
    
    class Category(models.IntegerChoices):
        OTHER       = 0, _("Прочее")
        ELECTRONICS = 1, _("Электроника")

    name        = models.CharField(max_length=255)
    boat        = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name="specifications")
    сategory    = models.IntegerField(choices=Category.choices)

    @classmethod
    def get_сategories(cls):
        сategories = cls.Category.choices
        return sorted(сategories, key=lambda tup: tup[1])

class BoatPrice(models.Model):
    class Type(models.IntegerChoices):
        DAY     = 0, _("Сутки")
        #WEEK    = 1, _("Неделя")

    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name="prices")
    type = models.IntegerField(choices=Type.choices, default=Type.DAY)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    @classmethod
    def get_types(cls):
        types = sorted(cls.Type.choices, key=lambda tup: tup[1])   
        return [list(e) for e in types]

    def clean(self):
        errors = []
        if self.end_date < self.start_date:
            errors.append(ValidationError(_('Окончание действия цены не должно быть раньше начала действия'), code="invalid_dates"))  

        existing_boat_prices = BoatPrice.objects.filter(
            boat=self.boat,
            type=self.type
        ).filter(
            Q(start_date__range=(self.start_date,self.end_date))|Q(end_date__range=(self.start_date,self.end_date))|Q(start_date__lt=self.start_date,end_date__gt=self.end_date)
        ).exclude(
            pk=self.pk
        )

        if existing_boat_prices.exists():
            errors.append(ValidationError(
                _('Период действия цены для типа "%(value)s" пересекается с другим периодом этого же типа'), 
                params={'value': self.get_type_display()},
                code="invalid_range"
            ))  

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(BoatPrice, self).save(*args, **kwargs)

    class Meta:
        ordering = ['start_date', 'end_date']


class BoatFile(models.Model):
    file = models.ImageField(upload_to=utils.get_file_path)
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE, related_name='files')

    def __str__(self):
        return '%s - %s' % (self.file, self.boat)

pre_save.connect(signals.verify_imagefile, sender=BoatFile)
pre_save.connect(signals.delete_old_file, sender=BoatFile)
post_save.connect(signals.compress_imagefile, sender=BoatFile)
post_delete.connect(signals.delete_file, sender=BoatFile)