from django.contrib import admin
from .models import Boat

class BoatAdmin(admin.ModelAdmin):
    pass

admin.site.register(Boat, BoatAdmin)