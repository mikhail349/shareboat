from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Boat, Manufacturer, Model, Tariff, Term


class TariffInline(admin.TabularInline):
    """Вкладка тарифов."""
    model = Tariff


class BoatAdmin(admin.ModelAdmin):
    """Модель админа лодки."""
    inlines = [TariffInline]


class ModelInline(admin.TabularInline):
    """Вкладка моделей лодок."""
    model = Model


class ManufacturerAdmin(admin.ModelAdmin):
    """Модель админа производителей."""
    inlines = [ModelInline]


class TariffAdmin(admin.ModelAdmin):
    """Модель админа тарифов."""
    fieldsets = (
        (None, {'fields': ('boat', 'name', 'price', 'active')}),
        ('Сезон', {'fields': ('start_date', 'end_date')}),
        ('Сроки', {'fields': ('duration', 'min', 'weight')}),
        ('Дни начала аренды', {
         'fields': ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')}),
    )
    list_display = (
        'name', 'boat', 'price', 'active',
        'start_date', 'end_date',
        'duration', 'min', 'weight',
        'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
    )
    list_filter = ('active',)
    date_hierarchy = 'start_date'
    readonly_fields = ('weight', )
    search_fields = ('name', 'boat__name',)


class TermAdmin(SummernoteModelAdmin):
    """Модель админа шаблона условий."""
    summernote_fields = ('content',)
    list_display = ('name', 'user')


admin.site.register(Boat, BoatAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Tariff, TariffAdmin)
admin.site.register(Term, TermAdmin)
