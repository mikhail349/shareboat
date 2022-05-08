from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from boat.models import Boat
from user.models import User

class Notification(models.Model):
    title = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    received_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    def __str__(self):
        return '%s - %s' % (self.title, self.text)

    class Meta:
        ordering = ['-pk']