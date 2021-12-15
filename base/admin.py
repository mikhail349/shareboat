from django.contrib import admin
from . import models

class BaseImageInline(admin.TabularInline):
    model = models.BaseImage

class BaseAdmin(admin.ModelAdmin):
    inlines = [BaseImageInline]

admin.site.register(models.Base, BaseAdmin)
