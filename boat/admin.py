from django.contrib import admin
from .models import Boat, BoatPrice, BoatPricePeriod, Manufacturer, Model, Tariff

class BoatPriceInline(admin.TabularInline):
    model = BoatPrice

class BoatAdmin(admin.ModelAdmin):
    inlines = [BoatPriceInline]

class ModelInline(admin.TabularInline):
    model = Model

class ManufacturerAdmin(admin.ModelAdmin):
    inlines = [ModelInline]

class TariffAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('boat', 'name', 'price')}),
        ('Сезон', {'fields': ('start_date', 'end_date')}),
        ('Сроки', {'fields': ('duration', 'min', 'max', 'weight')}),
        ('Дни начала аренды', {'fields': ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')}),
    )
    list_display = (
        'name', 'boat', 'price',
        'start_date', 'end_date',
        'duration', 'min', 'max', 'weight',
        'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
    )
    date_hierarchy = 'start_date'
    readonly_fields = ('weight', )
    search_fields = ('name', 'boat__name',)

admin.site.register(BoatPricePeriod)
admin.site.register(Boat, BoatAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Tariff, TariffAdmin)