from django.db import models
from django.contrib.auth import get_user_model
from booking.models import Booking

class Message(models.Model):
    User = get_user_model()

    text        = models.TextField()
    sender      = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_sender")  
    sent_at     = models.DateTimeField(auto_now_add=True)
    recipient   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="messages_as_recipient")
    read        = models.BooleanField(default=False)


class MessageBooking(Message):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name="messages")