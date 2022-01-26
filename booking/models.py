from http.client import ACCEPTED
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .exceptions import BookingDateRangeException, BookingDuplicatePendingException
from boat.models import Boat
from user.models import User

class Booking(models.Model):

    class Status(models.IntegerChoices):
        PENDING     = 0, _("Ожидание подтверждения")
        DECLINED    = -1, _("Отменена")
        ACCEPTED    = 1, _("Подтверждена")

    boat        = models.ForeignKey(Boat, on_delete=models.PROTECT, related_name='bookings')
    renter      = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings')
    status      = models.IntegerField(choices=Status.choices, default=Status.PENDING)

    start_date  = models.DateField()
    end_date    = models.DateField()
    total_sum   = models.DecimalField(max_digits=8, decimal_places=2)

    def clean(self):
        if self.pk is None:
            accepted_bookings_exist = Booking.objects.filter(
                boat=self.boat,
                status=self.Status.ACCEPTED
            ).filter(
                Q(start_date__range=(self.start_date,self.end_date))|Q(end_date__range=(self.start_date,self.end_date))|Q(start_date__lt=self.start_date,end_date__gt=self.end_date)
            ).exists()

            if accepted_bookings_exist:
                raise BookingDateRangeException()

            duplicate_bookings_exist = Booking.objects.filter(
                boat=self.boat,
                renter=self.renter,
                status=self.Status.PENDING
            ).filter(
                Q(start_date__range=(self.start_date,self.end_date))|Q(end_date__range=(self.start_date,self.end_date))|Q(start_date__lt=self.start_date,end_date__gt=self.end_date)
            ).exists()

            if duplicate_bookings_exist:
                raise BookingDuplicatePendingException()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Booking, self).save(*args, **kwargs)