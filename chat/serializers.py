from rest_framework import serializers
from .models import MessageBooking, MessageBoat, Message
from user.serializers import MessageUserSerializer

class MessageBookingSerializerSend(serializers.ModelSerializer):
    booking_id = serializers.IntegerField()

    class Meta:
        model = MessageBooking
        fields = ('text', 'booking_id')

class MessageSerializerList(serializers.ModelSerializer):
    sender = MessageUserSerializer()
    is_out = serializers.SerializerMethodField()

    def get_is_out(self, obj):
        return obj.sender == self.context['request'].user

    class Meta:
        model = Message
        fields = ('id', 'text', 'sender', 'is_out', 'sent_at')
