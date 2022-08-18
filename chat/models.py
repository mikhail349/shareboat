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

    def __str__(self):
        sender = self.sender or '[Системное сообщение]'
        return f'{sender}: {self.text}'

class SupportManager(models.Manager):
    def send_greetings(self, recipient):
        text = "<div>Вас приветствует SHAREBOAT.RU!</div><div>Здесь вы можете задать интересующий Вас вопрос.</div>"
        return self.create(recipient=recipient, text=text)

class MessageSupport(Message):

    objects = SupportManager() 

    def get_title(self):
        return 'Поддержка'

    def get_href(self):
        return reverse('chat:message')

class BookingManager(models.Manager):
    def send_initial_to_owner(self, booking):
        text = "<div>Новый запрос на бронирование</div>"
        return self.create(booking=booking, recipient=booking.boat.owner, text=text)

    def send_status(self, booking, recipient):
        text = f'<div>Статус бронирования изменился на "{booking.get_status_display()}"</div>'
        return self.create(booking=booking, recipient=recipient, text=text)        

    def remind_prepayment_to_renter(self, booking):
        text = f'<div>Не забудьте внести предоплату.</div>'
        return self.create(booking=booking, recipient=booking.renter, text=text)    

    def remind_prepayment_to_owner(self, booking):
        text = f'<div>Не забудьте сменить статус на "Оплата получена", если Вы получили предоплату.</div>'
        return self.create(booking=booking, recipient=booking.boat.owner, text=text) 

class MessageBooking(Message):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="messages")
    objects = BookingManager()

    def get_title(self):
        return self.booking.boat.name

    def get_href(self):
        return reverse('chat:booking', kwargs={'pk': self.booking.pk})

class BoatManager(models.Manager):
    def send_published_to_owner(self, boat):
        text = "<div>Лодка опубликована!</div>"
        return self.create(boat=boat, recipient=boat.owner, text=text)

    def send_declined_to_owner(self, boat, comment):
        text = f"<div>Лодка не прошла модерацию.</div><div>Объявление не соответствует правилам сервиса: {comment}</div>"
        return self.create(boat=boat, recipient=boat.owner, text=text)

class MessageBoat(Message):
    
    class RejectionReason(models.IntegerChoices):
        OTHER = 0, "Прочее"
    
    boat = models.ForeignKey(Boat, on_delete=models.PROTECT, related_name="messages")
    objects = BoatManager()

    def get_title(self):
        return self.boat.name

    def get_href(self):
        return reverse('chat:boat', kwargs={'pk': self.boat.pk})

    @classmethod
    def get_rejection_reasons(cls):
        types = cls.RejectionReason.choices
        return sorted(types, key=lambda tup: tup[1])