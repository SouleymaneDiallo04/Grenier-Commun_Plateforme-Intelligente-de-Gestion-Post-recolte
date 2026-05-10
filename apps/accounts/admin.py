from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPCode

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'nom_complet', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'pays']
    search_fields = ['email', 'nom', 'prenom', 'telephone']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations', {'fields': ('nom', 'prenom', 'telephone', 'avatar')}),
        ('Rôle & Langue', {'fields': ('role', 'langue_preferee', 'pays', 'region')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'nom', 'prenom', 'role', 'password1', 'password2')}),
    )

@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'telephone', 'est_utilise', 'cree_le', 'expire_le']
