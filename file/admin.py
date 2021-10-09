from django.contrib import admin

from .models import File, AssetFile

class FileAdmin(admin.ModelAdmin):
      exclude = ('name',)

class AssetFileAdmin(FileAdmin):
    pass

#admin.site.register(File, FileAdmin)
admin.site.register(AssetFile, AssetFileAdmin)
