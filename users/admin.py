from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()

# класс-редактор
# class CustomUserAdmin(UserAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ['username', 'email',]
#     list_display_links = ['username', 'email', ]
#
# admin.site.register(CustomUser, CustomUserAdmin)


# users/admin.py
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_staff')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
