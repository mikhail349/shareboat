from django.contrib import admin

from .models import Message, MessageBooking, MessageBoat, MessageSupport


class MessageAdmin(admin.ModelAdmin):
    model = Message
    list_display = ('sender', 'recipient', 'text', 'sent_at')


class MessageBookingAdmin(MessageAdmin):
    model = MessageBooking
    list_display = MessageAdmin.list_display + ('booking',)


class MessageBoatAdmin(MessageAdmin):
    model = MessageBoat
    list_display = MessageAdmin.list_display + ('boat',)


admin.site.register(MessageBooking, MessageBookingAdmin)
admin.site.register(MessageBoat, MessageBoatAdmin)
admin.site.register(MessageSupport)
