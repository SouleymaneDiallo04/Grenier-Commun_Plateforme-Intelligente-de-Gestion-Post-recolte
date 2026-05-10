from django.contrib import admin
from .models import Silo, Commune, Denree, Depot, Retrait, AlerteSilo

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['nom', 'region', 'pays']
    search_fields = ['nom', 'region']

@admin.register(Denree)
class DenreeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nom_wolof', 'humidite_max', 'actif']

@admin.register(Silo)
class SiloAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'commune', 'gestionnaire', 'taux_remplissage', 'statut', 'sante']
    list_filter = ['statut', 'sante', 'commune__region']
    search_fields = ['nom', 'code', 'commune__nom']

@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ['numero_recu', 'agriculteur', 'silo', 'denree', 'quantite_initiale_kg', 'statut', 'date_depot']
    list_filter = ['statut', 'denree']
    search_fields = ['numero_recu', 'agriculteur__nom', 'agriculteur__email']

admin.site.register(Retrait)
admin.site.register(AlerteSilo)
