from asyncore import read
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from boat.models import Boat
from booking.models import Booking

class Message(models.Model):
    User = get_user_model()

    text        = models.TextField()
    sender      = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_sender", null=True, blank=True)  
    sent_at     = models.DateTimeField(auto_now_add=True)
    recipient   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_recipient", null=True, blank=True)
    read        = models.BooleanField(default=False)

    def get_title(self):
        return ''

    def get_href(self):
        return reverse('chat:message')

    def get_badge(self):
        return '<div class="badge bg-warning text-primary">Shareboat</div>'

    def __str__(self):
        sender = self.sender or '[Системное сообщение]'
        return f'{sender}: {self.text}'

class MessageSupport(Message):
    def get_title(self):
        return 'Поддержка'

    def get_href(self):
        return reverse('chat:message')

    def get_badge(self):
        return '<div class="badge bg-warning text-primary">Поддержка</div>'     

class BookingManager(models.Manager):
    def get_link(self, booking):
        return '<a class="btn btn-primary mt-2" href="%s" role="button">Перейти в бронь</a>' % reverse('booking:view', kwargs={'pk': booking.pk})

    def send_initial_msg(self, booking):
        text = '<div>Новый запрос</div><a class="btn btn-primary mt-2" href="%s" role="button">Перейти в бронь</a>' % reverse('booking:view', kwargs={'pk': booking.pk})
        return self.create(booking=booking, recipient=booking.boat.owner, text=text)

    def send_status_to_renter(self, booking):
        def get_msg():
            if booking.status in [Booking.Status.ACCEPTED, Booking.Status.DECLINED]:
                return f'Бронирование {booking.get_status_display().lower()}.'
            if booking.status == Booking.Status.PREPAYMENT_REQUIRED:
                return f'Бронирование подтверждено. {booking.get_status_display()}.'
            return ''

        text = f'<div>{get_msg()}</div>{self.get_link(booking)}'
        return self.create(booking=booking, recipient=booking.renter, text=text)        

class MessageBooking(Message):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="messages")
    objects = BookingManager()

    def get_title(self):
        return self.booking.boat.name

    def get_href(self):
        return reverse('chat:booking', kwargs={'pk': self.booking.pk})

    def get_badge(self):
        return '<div class="badge bg-light text-primary">Бронирование</div>' 

class MessageBoat(Message):
    
    class RejectionReason(models.IntegerChoices):
        OTHER = 0, "Прочее"
    
    boat = models.ForeignKey(Boat, on_delete=models.PROTECT, related_name="messages")

    def get_title(self):
        return self.boat.name

    def get_href(self):
        return reverse('chat:boat', kwargs={'pk': self.boat.pk})

    def get_badge(self):
        return '<div class="badge bg-light text-primary">Лодка</div>' 

    @classmethod
    def get_rejection_reasons(cls):
        types = cls.RejectionReason.choices
        return sorted(types, key=lambda tup: tup[1])