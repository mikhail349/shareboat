from asyncore import read
from django.db import models
from django.contrib.auth import get_user_model

from boat.models import Boat
from booking.models import Booking

class Message(models.Model):
    User = get_user_model()

    text        = models.TextField()
    sender      = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_sender", null=True, blank=True)  
    sent_at     = models.DateTimeField(auto_now_add=True)
    recipient   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_recipient", null=True, blank=True)
    read        = models.BooleanField(default=False)

    def __str__(self):
        sender = self.sender or '[Системное сообщение]'
        return f'{sender}: {self.text}'

class MessageBooking(Message):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="messages")

class MessageBoat(Message):
    
    class RejectionReason(models.IntegerChoices):
        OTHER = 0, "Прочее"
    
    boat = models.ForeignKey(Boat, on_delete=models.PROTECT, related_name="messages")

    @classmethod
    def get_rejection_reasons(cls):
        types = cls.RejectionReason.choices
        return sorted(types, key=lambda tup: tup[1])