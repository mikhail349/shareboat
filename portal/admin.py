from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html

from .models import Category

class CategoryAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('name', 'url', 'full_path', 'parent', 'published')
    readonly_fields = ('full_path',)

    #def show_url(self, obj):
    #    return format_html('<a href="{url}">{url}</a>', url=obj.url)

admin.site.register(Category, CategoryAdmin)


