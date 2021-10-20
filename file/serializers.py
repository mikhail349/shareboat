import os
from rest_framework import serializers
from .models import AssetFile 

class AssetFileSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source="file.url")
    #filename = serializers.CharField(max_length=255, source="file.name")
    filename = serializers.SerializerMethodField()

    def get_filename(self, obj):
        return os.path.basename(obj.file.name)
    
    #url = serializers.SerializerMethodField() 
    #def get_url(self, obj):
        #request = self.context.get('request')
        #return request.build_absolute_uri(obj.file.url)

    class Meta:
        model = AssetFile
        fields = ('id', 'url', 'filename')
