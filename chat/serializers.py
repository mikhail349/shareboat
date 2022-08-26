from rest_framework import serializers

from user.models import User
from .models import MessageBooking, Message
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
        if self.context.get('is_support'):
            return obj.sender is None
        return obj.sender == self.context['request'].user

    class Meta:
        model = Message
        fields = ('id', 'text', 'sender', 'is_out', 'sent_at')

class PalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'avatar_sm')

class ChatSerializerList(serializers.ModelSerializer):

    sender = PalSerializer()
    recipient = PalSerializer()
    get_title = serializers.CharField()
    get_href = serializers.URLField()
    badge = serializers.CharField()

    class Meta:
        model = Message
        fields = ('get_title', 'get_href', 'text', 'sender', 'sent_at', 'badge', 'recipient', 'read')
