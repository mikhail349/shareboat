from django.contrib import admin

from .models import AssetFile

class AssetFileAdmin(admin.ModelAdmin):
    pass

admin.site.register(AssetFile, AssetFileAdmin)