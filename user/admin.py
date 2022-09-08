from django.contrib import admin
from django.utils.translation import gettext as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, TelegramUser


class TelegramUserInline(admin.StackedInline):
    model = TelegramUser


class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with \
    no email and last_name fields."""

    fieldsets = (
        (None, {'fields': ('email', 'email_confirmed', 'password')}),
        (_('Personal info'), {'fields': ('first_name',)}),
        (_('Уведомления'), {'fields': ('email_notification',)}),
        (_('Интерфейс'), {'fields': ('use_dark_theme',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'email_confirmed', 'first_name', 'is_staff')
    search_fields = ('email', 'first_name',)
    ordering = ('email',)
    inlines = (TelegramUserInline,)


admin.site.register(User, UserAdmin)
