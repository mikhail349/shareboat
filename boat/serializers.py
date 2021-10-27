import os
from rest_framework import serializers
from .models import Boat, BoatFile


class BoatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boat
        fields = ('id', 'name', 'length', 'width', 'draft')

class BoatFileSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source="file.url")
    filename = serializers.SerializerMethodField()

    def get_filename(self, obj):
        return os.path.basename(obj.file.name)

    class Meta:
        model = BoatFile
        fields = ('id', 'url', 'filename')
