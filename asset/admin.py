from django.contrib import admin
from .models import Asset

class AssetAdmin(admin.ModelAdmin):
    pass

admin.site.register(Asset, AssetAdmin)