import imp
from rest_framework import serializers
from .models import User

class MessageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'avatar')