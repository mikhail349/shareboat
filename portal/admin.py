from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Category, Article


class CategoryAdmin(SummernoteModelAdmin):
    summernote_fields = ('description',)
    list_display = ('name', 'url', 'full_path', 'parent', 'published')
    readonly_fields = ('full_path',)


class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('name', 'url', 'full_path',
                    'preview_text', 'category', 'published')
    readonly_fields = ('created_at', 'updated_at', 'full_path')

    def get_changeform_initial_data(self, request):
        return {'creator': request.user}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
