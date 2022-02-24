from rest_framework import serializers
from .models import MessageBooking

class MessageBookingSerializerSend(serializers.ModelSerializer):
    booking_id = serializers.IntegerField()

    class Meta:
        model = MessageBooking
        fields = ('text', 'booking_id')