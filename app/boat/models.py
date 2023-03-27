from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import (DecimalField, Exists, F, OuterRef, Prefetch, Q,
                              Value)
from django.db.models.functions import Cast
from django.db.models.signals import post_save, pre_save
from django.utils.translation import gettext_lazy as _

from base.models import Base
from file import signals, utils

User = get_user_model()


class ActiveBoatManager(models.Manager):
    """Менеджер активных лодок."""
    def get_queryset(self):
        return super().get_queryset().exclude(status=Boat.Status.DELETED)


class PublishedBoatManager(models.Manager):
    """Менеджер опубликованных лодок."""
    def get_queryset(self):
        return super().get_queryset().filter(status=Boat.Status.PUBLISHED)


class BoatQuerySet(models.QuerySet):
    """QuerySet лодки."""
    def annotate_in_fav(self, user: User):  # type: ignore
        """Добавить поле, добавлена ли лодка в избранное.

        Args:
            user: пользователь

        """
        if user.is_authenticated:  # type: ignore
            return self.annotate(
                in_fav=Exists(BoatFav.objects.filter(boat__pk=OuterRef('pk'),
                                                     user=user))
            )
        return self.annotate(in_fav=Value(False))

    def prefetch_actual_tariffs(self):
        """Предварительно выбрать активные тарифы с ценой за день."""
        actual_tariffs = Tariff.objects.active_gte_now().annotate(
            price_per_day=Cast(F('price') / F('duration'),
                               DecimalField(max_digits=6, decimal_places=0))
        ).order_by('start_date', 'price_per_day')
        return self.prefetch_related(
            Prefetch('tariffs', queryset=actual_tariffs,
                     to_attr='actual_tariffs')
        )

    def active(self):
        """Исключить удаленные лодки."""
        return self.exclude(status=Boat.Status.DELETED)


class TariffQuerySet(models.QuerySet):
    """QuerySet тарифа."""
    def active_gte_now(self):
        """
        Отфильтровать активные тарифы, которые действуют сейчас или
        будут действовать в будущем.
        """
        now = datetime.now()
        return self.filter(
            Q(active=True),
            Q(start_date__lte=now, end_date__gte=now) | Q(start_date__gt=now)
        )


class Manufacturer(models.Model):
    """Модель производителя лодок."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Model(models.Model):
    """Модель моделей лодок."""
    name = models.CharField(max_length=255)
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.PROTECT, related_name="models")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Term(models.Model):
    """Модель шаблонов условий."""
    name = models.CharField('Название шаблона', max_length=255)
    content = models.TextField('Текст условий')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="term_templates",
                             null=True, blank=True,
                             verbose_name='Пользователь')

    def __str__(self):
        return self.name


class Boat(models.Model):
    """Модель лодки."""
    class Meta:
        permissions = [
            ('view_boats_on_moderation', 'Can view boats on moderation'),
            ('moderate_boats', 'Can moderate boats'),
            ('view_my_boats', 'Can view my boats'),
        ]

    class Status(models.IntegerChoices):
        """Статусы лодки."""
        DELETED = -2, _("Удалена")
        DECLINED = -1, _("Отклонена")
        SAVED = 0, _("Сохранена")
        ON_MODERATION = 1, _("На проверке")
        PUBLISHED = 2, _("Опубликована")

    class Type(models.IntegerChoices):
        """Типы лодки."""
        SAILING_YACHT = 0, _("Парусная яхта")
        MOTOR_BOAT = 1, _("Катер/моторная лодка")
        BOAT = 2, _("Лодка")
        GULET = 3, _("Гулет")
        JET_SKI = 4, _("Гидроцикл")
        MOTOR_YACHT = 5, _("Моторная яхта")
        HOUSE_BOAT = 6, _("Хаусбот")
        CATAMARAN = 7, _("Катамаран")
        TRIMARAN = 8, _("Тримаран")

    name = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="boats")
    model = models.ForeignKey(
        Model, on_delete=models.PROTECT, related_name="boats")
    status = models.IntegerField(choices=Status.choices, default=Status.SAVED)

    issue_year = models.IntegerField(null=True, blank=True,
                                     validators=[
                                        MinValueValidator(1900),
                                        MaxValueValidator(2999)
                                     ])
    length = models.DecimalField(max_digits=5, decimal_places=2, validators=[
                                 MinValueValidator(Decimal('0.1'))])
    width = models.DecimalField(max_digits=4, decimal_places=2, validators=[
                                MinValueValidator(Decimal('0.1'))])
    draft = models.DecimalField(max_digits=3, decimal_places=2, validators=[
                                MinValueValidator(Decimal('0.1'))])
    capacity = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(99)])
    type = models.IntegerField(choices=Type.choices)
    prepayment_required = models.BooleanField(default=False)
    term = models.ForeignKey(Term, on_delete=models.SET_NULL,
                             related_name="boats", null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)

    base = models.ForeignKey(Base, on_delete=models.SET_NULL,
                             related_name="boats", null=True, blank=True)

    objects = models.Manager.from_queryset(BoatQuerySet)()
    active = ActiveBoatManager()
    published = PublishedBoatManager.from_queryset(BoatQuerySet)()

    @property
    def is_active(self) -> bool:
        """Свойство - активна ли лодка (или удалена).

        Returns:
            bool: активна / удалена

        """
        return self.status != self.Status.DELETED

    @property
    def is_published(self) -> bool:
        """Свойство - опубликована ли лодка.

        Returns:
            bool: опубликована / не опубликована

        """
        return self.status == self.Status.PUBLISHED

    def get_full_name(self) -> str:
        """Получить полное название лодки с производителем и моделью.

        Returns:
            str: название лодки в формате `производитель модель "название"`

        """
        manufacturer_name = self.model.manufacturer.name
        return f'{manufacturer_name} {self.model.name} "{self.name}"'

    def clean(self):
        if self.text:
            self.text = self.text.strip()
        if self.text == "":
            self.text = None
        if self.issue_year == "":
            self.issue_year = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Boat, self).save(*args, **kwargs)

    def is_motor_boat(self) -> bool:
        """Является ли лодка моторной.

        Returns:
            bool: да / нет

        """
        return self.type in self.get_motor_boat_types()

    def is_comfort_boat(self) -> bool:
        """Имеет ли лодка сан. узлы, каюты, спальные места.

        Returns:
            bool: да / нет

        """
        return self.type in self.get_comfort_boat_types()

    def is_custom_location(self) -> bool:
        """Заданы ли координаты лодки вручную.

        Returns:
            bool: да / нет

        """
        try:
            self.coordinates
            return True
        except BoatCoordinates.DoesNotExist:
            return False

    @classmethod
    def get_motor_boat_types(cls) -> list[tuple[int, str]]:
        """Получить перечень моторных типов лодки.

        Returns:
            list[Type]: перечень моторных типов лодки

        """
        return [
            cls.Type.SAILING_YACHT,
            cls.Type.MOTOR_BOAT,
            cls.Type.GULET,
            cls.Type.JET_SKI,
            cls.Type.MOTOR_YACHT,
            cls.Type.HOUSE_BOAT,
            cls.Type.CATAMARAN,
            cls.Type.TRIMARAN
        ]

    @classmethod
    def get_comfort_boat_types(cls) -> list[tuple[int, str]]:
        """Получить перечень комфортных типов лодки.

        Returns:
            list[Type]: перечень комфортных типов лодки

        """
        return [
            cls.Type.SAILING_YACHT,
            cls.Type.GULET,
            cls.Type.MOTOR_YACHT,
            cls.Type.HOUSE_BOAT,
            cls.Type.CATAMARAN,
            cls.Type.TRIMARAN
        ]

    @classmethod
    def get_types(cls) -> list[tuple[int, str]]:
        """Получить перечень типов лодки, отсортированных по названию.

        Returns:
            list[Type]

        """
        types = cls.Type.choices
        return sorted(types, key=lambda tup: tup[1])

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())


class MotorBoat(models.Model):
    """Модель моторной лодки."""
    boat = models.OneToOneField(Boat, on_delete=models.CASCADE,
                                primary_key=True, related_name="motor_boat")
    motor_amount = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(9)])
    motor_power = models.DecimalField(max_digits=5, decimal_places=1,
                                      validators=[
                                        MinValueValidator(Decimal('0.1'))
                                      ])


class ComfortBoat(models.Model):
    """Модель комфортной лодки."""
    boat = models.OneToOneField(Boat, on_delete=models.CASCADE,
                                primary_key=True, related_name="comfort_boat")
    berth_amount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)])
    extra_berth_amount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)], default=0)
    cabin_amount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)])
    bathroom_amount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9)])


class BoatCoordinates(models.Model):
    """Модель коррдинат лодки."""
    boat = models.OneToOneField(Boat, on_delete=models.CASCADE,
                                primary_key=True, related_name="coordinates")
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    state = models.CharField(max_length=255, db_index=True)


class Specification(models.Model):
    """Модель спецификации лодки."""

    class Category(models.IntegerChoices):
        """Категории спецификации лодки."""
        OTHER = 0, _("Прочее")
        ELECTRONICS = 1, _("Электроника")

    name = models.CharField(max_length=255)
    boat = models.ForeignKey(
        Boat, on_delete=models.CASCADE, related_name="specifications")
    сategory = models.IntegerField(choices=Category.choices)

    @classmethod
    def get_сategories(cls) -> list[Category]:
        """Получить перечень категорий, отсортированных по названию.

        Returns:
            list[Category]

        """
        сategories = cls.Category.choices
        return sorted(сategories, key=lambda tup: tup[1])


def get_upload_to(instance: models.Model, filename: str) -> str:
    """Получить путь сохранения файла.

    Args:
        instance: инстанс модели
        filename: имя файла

    Returns:
        str

    """
    return utils.get_file_path(instance, filename, 'boat/')


class BoatFile(models.Model):
    """Модель файлов лодки."""
    file = models.ImageField(upload_to=get_upload_to)
    boat = models.ForeignKey(
        Boat, on_delete=models.CASCADE, related_name='files')


pre_save.connect(signals.verify_imagefile, sender=BoatFile)
post_save.connect(signals.compress_imagefile, sender=BoatFile)


class BoatFav(models.Model):
    """Модель отметки лодка нравится."""
    boat = models.ForeignKey(
        Boat, on_delete=models.PROTECT, related_name='favs')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="fav_boats")

    class Meta:
        unique_together = [['boat', 'user']]


class Tariff(models.Model):
    """Модель тарифа лодки."""
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE,
                             related_name="tariffs", verbose_name='Лодка')
    active = models.BooleanField('Активен', default=False)
    start_date = models.DateField('Начало действия')
    end_date = models.DateField('Окончание действия')

    name = models.CharField('Название тарифа', max_length=255)
    duration = models.IntegerField(
        'Продолжительность, дней',
        validators=[MinValueValidator(1)],
        help_text='Напр.: неделя - 7, выходные - 3, сутки - 1')
    min = models.IntegerField(
        'Минимальный срок аренды',
        validators=[MinValueValidator(1)],
        help_text='Минимальный срок аренды')
    weight = models.IntegerField(
        'Вес тарифа', help_text='Рассчитывается автоматически')

    mon = models.BooleanField('Пн.', default=False)
    tue = models.BooleanField('Вт.', default=False)
    wed = models.BooleanField('Ср.', default=False)
    thu = models.BooleanField('Чт.', default=False)
    fri = models.BooleanField('Пт.', default=False)
    sat = models.BooleanField('Сб.', default=False)
    sun = models.BooleanField('Вс.', default=False)

    price = models.DecimalField('Цена', max_digits=8, decimal_places=2,
                                validators=[
                                    MinValueValidator(Decimal("0.01"))
                                ])

    objects = models.Manager.from_queryset(TariffQuerySet)()

    def clean(self):
        errors = {}
        non_field_errors = []

        if True not in [self.mon, self.tue, self.wed, self.thu, self.fri,
                        self.sat, self.sun]:
            non_field_errors.append(
                'Необходимо указать хотя бы один день начала аренды')

        if self.start_date > self.end_date:
            errors['start_date'] = ['Должно быть раньше окончания действия']

        if non_field_errors:
            errors[NON_FIELD_ERRORS] = non_field_errors

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.weight = self.duration * self.min
        self.full_clean()
        super(Tariff, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        ordering = ['start_date', 'end_date', '-weight']
