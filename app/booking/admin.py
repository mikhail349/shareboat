from django.contrib import admin

from .models import Booking, Prepayment, BoatInfo, BoatInfoCoordinates


class PrepaymentInline(admin.StackedInline):
    model = Prepayment


class BookingAdmin(admin.ModelAdmin):
    inlines = [PrepaymentInline]


admin.site.register(Booking, BookingAdmin)
admin.site.register(BoatInfo)
admin.site.register(BoatInfoCoordinates)
