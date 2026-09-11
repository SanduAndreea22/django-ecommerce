from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # câmpurile care apar în lista din admin
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    # câmpurile din formularul de editare user
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'description', 'image')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # is_staff/is_superuser nu apar aici intenționat: un cont cu drept de "add
    # customuser" nu trebuie să poată crea direct un superuser din formularul
    # de creare. Permisiunile astea se acordă doar din formularul de editare
    # (fieldsets), unde Django restricționează schimbarea is_superuser doar la
    # utilizatori care sunt ei înșiși superuser.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )

# Înregistrează modelul în admin
admin.site.register(CustomUser, CustomUserAdmin)

