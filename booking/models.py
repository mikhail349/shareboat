from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .exceptions import BookingDateRangeException, \
                        BookingDuplicatePendingException
from boat.models import Boat, Model, Base
from user.models import User


class BookingQuerySet(models.QuerySet):
    def in_range(self, start_date, end_date):
        return self.filter(
            Q(start_date__range=(start_date, end_date)) |
            Q(end_date__range=(start_date, end_date)) |
            Q(start_date__lt=start_date, end_date__gt=end_date)
        )

    def blocked_in_range(self, start_date, end_date):
        return self.filter(status__in=Booking.BLOCKED_STATUSES) \
                   .in_range(start_date, end_date)

    def filter_by_status(self, status):
        if status == 'pending':
            return self.filter(status__in=Booking.PENDING_STATUSES)
        if status == 'active':
            return self.filter(status__in=Booking.ACTIVE_STATUSES)
        elif status == 'done':
            return self.filter(status__in=Booking.DONE_STATUSES)
        return self


class Booking(models.Model):

    class Status(models.IntegerChoices):
        PENDING = 0, _("Ожидание подтверждения")
        DECLINED = -1, _("Отменено")
        ACCEPTED = 1, _("Подтверждено")
        PREPAYMENT_REQUIRED = 2, _("Ожидание предоплаты")
        ACTIVE = 3, _("Активно")
        DONE = 4, _("Завершено")

    BLOCKED_STATUSES = [Status.ACCEPTED,
                        Status.PREPAYMENT_REQUIRED,
                        Status.ACTIVE,
                        Status.DONE]

    PENDING_STATUSES = [Status.PENDING, ]
    ACTIVE_STATUSES = [Status.ACCEPTED,
                       Status.PREPAYMENT_REQUIRED,
                       Status.ACTIVE]

    DONE_STATUSES = [Status.DONE, Status.DECLINED]

    STATUSES_CAN_BE_DECLINED = [Status.PENDING, Status.PREPAYMENT_REQUIRED]

    boat = models.ForeignKey(
        Boat, on_delete=models.PROTECT, related_name='bookings')
    renter = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='bookings')
    status = models.IntegerField(
        choices=Status.choices, default=Status.PENDING)

    start_date = models.DateField()
    end_date = models.DateField()
    total_sum = models.DecimalField(max_digits=8, decimal_places=2)
    spec = models.JSONField(null=True, blank=True)

    objects = models.Manager.from_queryset(BookingQuerySet)()

    def clean(self):
        if self.pk is None:
            accepted_bookings_exist = \
                Booking.objects \
                       .filter(boat=self.boat) \
                       .blocked_in_range(self.start_date, self.end_date) \
                       .exists()

            if accepted_bookings_exist:
                raise BookingDateRangeException()

            duplicate_bookings_exist = Booking.objects.filter(
                boat=self.boat,
                renter=self.renter,
                status=self.Status.PENDING
            ).in_range(self.start_date, self.end_date).exists()

            if duplicate_bookings_exist:
                raise BookingDuplicatePendingException()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Booking, self).save(*args, **kwargs)

    def __str__(self):
        return f'Бронь № {self.pk} - {self.boat}'


class Prepayment(models.Model):
    booking = models.OneToOneField(
        Booking, primary_key=True, on_delete=models.CASCADE)
    until = models.DateTimeField()


class BoatInfo(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE,
                                   primary_key=True, related_name="boat_info")
    prepayment_required = models.BooleanField()
    term_content = models.TextField(null=True, blank=True)

    owner = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="requests")
    model = models.ForeignKey(
        Model, on_delete=models.PROTECT, related_name="bookings")
    type = models.IntegerField(choices=Boat.Type.choices)
    base = models.ForeignKey(Base, on_delete=models.PROTECT,
                             related_name="bookings", null=True, blank=True)
    photo = models.ImageField()
    spec = models.JSONField(null=True, blank=True)


class BoatInfoCoordinates(models.Model):
    boat_info = models.OneToOneField(BoatInfo, on_delete=models.CASCADE,
                                     primary_key=True,
                                     related_name="coordinates")
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    state = models.CharField(max_length=255, db_index=True)
