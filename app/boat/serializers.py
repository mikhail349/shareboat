import os

from rest_framework import serializers

from .models import Boat, BoatFile, Model


class ModelSerializer(serializers.ModelSerializer):
    """Сериализатор модели лодки."""
    class Meta:
        model = Model
        fields = ('id', 'name')


class BoatSerializer(serializers.ModelSerializer):
    """Сериализатор лодки."""
    class Meta:
        model = Boat
        fields = ('id', 'name', 'length', 'width', 'draft', 'capacity')


class BoatFileSerializer(serializers.ModelSerializer):
    """Сериализатор файла лодки."""
    url = serializers.URLField(source="file.url")
    filename = serializers.SerializerMethodField()

    def get_filename(self, obj: BoatFile) -> str:
        """Получить имя файла.

        Args:
            obj: инстанс файла лодки

        Returns:
            str

        """
        return os.path.basename(obj.file.name)

    class Meta:
        model = BoatFile
        fields = ('id', 'url', 'filename')
