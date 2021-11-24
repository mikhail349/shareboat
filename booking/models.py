from django.db import models
from django.utils.translation import gettext_lazy as _

from boat.models import Boat
from user.models import User

class Booking(models.Model):

    class Status(models.IntegerChoices):
        PENDING     = 0, _("На рассмотрении")
        DECLINED    = -1, _("Отклонено")
        APPROVED    = 1, _("Подтверждено")

    boat        = models.ForeignKey(Boat, on_delete=models.PROTECT, related_name='bookings')
    renter      = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings')
    status      = models.IntegerField(choices=Status.choices, default=Status.PENDING)

    start_date  = models.DateField()
    end_date    = models.DateField()
    price       = models.DecimalField(max_digits=8, decimal_places=2)