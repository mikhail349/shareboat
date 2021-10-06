from django.contrib import admin
from django.utils.translation import gettext as _
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User

class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email and last_name fields."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', )}),
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
    list_display = ('email', 'first_name', 'is_staff')
    search_fields = ('email', 'first_name',)
    ordering = ('email',)

admin.site.register(User, UserAdmin)