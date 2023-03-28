from django.contrib import admin

from .models import BoatInfo, BoatInfoCoordinates, Booking, Prepayment


class PrepaymentInline(admin.StackedInline):
    """Вкладка предоплаты."""
    model = Prepayment


class BookingAdmin(admin.ModelAdmin):
    """Модель админа бронирования."""
    inlines = [PrepaymentInline]


admin.site.register(Booking, BookingAdmin)
admin.site.register(BoatInfo)
admin.site.register(BoatInfoCoordinates)
