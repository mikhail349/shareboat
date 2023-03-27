from django.contrib import admin

from . import models


class BaseImageInline(admin.TabularInline):
    """Вкладка с фотографиями Базы."""
    model = models.BaseImage


class BaseAdmin(admin.ModelAdmin):
    """Модель админа для Базы."""
    inlines = [BaseImageInline]


admin.site.register(models.Base, BaseAdmin)
