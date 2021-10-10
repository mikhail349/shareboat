from django.db import models
from user.models import User

class Asset(models.Model):
    name    = models.CharField(max_length=255)
    owner   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assets")
    
    def __str__(self):
        return self.name

#class Boat(Asset):
#    pass