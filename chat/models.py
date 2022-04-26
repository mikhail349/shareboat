from asyncore import read
from django.db import models
from django.contrib.auth import get_user_model
from booking.models import Booking

class Message(models.Model):
    User = get_user_model()

    text        = models.TextField()
    sender      = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_sender")  
    sent_at     = models.DateTimeField(auto_now_add=True)
    recipient   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_recipient")
    by_system   = models.BooleanField(default=False)
    read        = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender}: {self.text}'

class MessageBooking(Message):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="messages")