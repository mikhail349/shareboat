from rest_framework import serializers

from user.serializers import MessageUserSerializer

from .models import Message, MessageBooking


class MessageBookingSerializerSend(serializers.ModelSerializer):
    booking_id = serializers.IntegerField()

    class Meta:
        model = MessageBooking
        fields = ('text', 'booking_id')


class MessageSerializerList(serializers.ModelSerializer):
    sender = MessageUserSerializer()
    is_out = serializers.SerializerMethodField()

    def get_is_out(self, obj):
        if self.context.get('is_support'):
            return obj.sender is None
        return obj.sender == self.context['request'].user

    class Meta:
        model = Message
        fields = ('id', 'text', 'sender', 'is_out', 'sent_at')
