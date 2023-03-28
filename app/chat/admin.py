from django.contrib import admin

from .models import Message, MessageBoat, MessageBooking, MessageSupport


class MessageAdmin(admin.ModelAdmin):
    """Админ-модель сообщения."""
    model = Message
    list_display = ['sender', 'recipient', 'text', 'sent_at']


class MessageBookingAdmin(MessageAdmin):
    """Админ-модель сообщения по бронированию."""
    model = MessageBooking
    list_display = MessageAdmin.list_display + ['booking']


class MessageBoatAdmin(MessageAdmin):
    """Админ-модель сообщения по лодке."""
    model = MessageBoat
    list_display = MessageAdmin.list_display + ['boat']


admin.site.register(MessageBooking, MessageBookingAdmin)
admin.site.register(MessageBoat, MessageBoatAdmin)
admin.site.register(MessageSupport)
