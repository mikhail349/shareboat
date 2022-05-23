from django.contrib import admin
from django.db import models
from .models import Boat, BoatPrice, Manufacturer, Model

class BoatPriceInline(admin.TabularInline):
    model = BoatPrice

class BoatAdmin(admin.ModelAdmin):
    inlines = [BoatPriceInline]

class ModelInline(admin.TabularInline):
    model = Model

class ManufacturerAdmin(admin.ModelAdmin):
    inlines = [ModelInline]

admin.site.register(Boat, BoatAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)