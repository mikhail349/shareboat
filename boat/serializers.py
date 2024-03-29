import os

from rest_framework import serializers

from .models import Boat, BoatFile, Model


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ('id', 'name')


class BoatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boat
        fields = ('id', 'name', 'length', 'width', 'draft', 'capacity')


class BoatFileSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source="file.url")
    filename = serializers.SerializerMethodField()

    def get_filename(self, obj):
        return os.path.basename(obj.file.name)

    class Meta:
        model = BoatFile
        fields = ('id', 'url', 'filename')
