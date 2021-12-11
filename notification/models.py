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

    def get_type(self):
        return self.__class__.__name__

    class Meta:
        ordering = ['-pk']

class BoatDeclinedModeration(Notification):
    
    class REASON(models.IntegerChoices):
        OTHER = 0, _("Прочее")

    boat    = models.OneToOneField(Boat, on_delete=models.CASCADE, related_name="declined_moderation")
    reason  = models.IntegerField(choices=REASON.choices)
    comment = models.TextField(null=True, blank=True)

    @classmethod
    def get_reasons(cls):
        types = cls.REASON.choices
        return sorted(types, key=lambda tup: tup[1])
