from django.contrib import admin
from django.db import models
from .models import Boat, BoatPrice

class BoatPriceInline(admin.TabularInline):
    model = BoatPrice

class BoatAdmin(admin.ModelAdmin):
    inlines = [BoatPriceInline]

admin.site.register(Boat, BoatAdmin)