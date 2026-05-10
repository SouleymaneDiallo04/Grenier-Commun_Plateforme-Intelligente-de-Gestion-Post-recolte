"""
Script de setup — crée toute l'arborescence du projet Grenier Commun
Exécuter avec : python setup_project.py
"""
import os

# ─── Arborescence complète ────────────────────────────────────────────────────
DIRS = [
    "config",
    "apps/core/management/commands",
    "apps/core/templatetags",
    "apps/accounts",
    "apps/silos/templatetags",
    "apps/agriculteurs",
    "apps/warrantage",
    "apps/marche",
    "apps/imf",
    "apps/notifications",
    "apps/traduction",
    "apps/intelligence",
    "apps/administration",
    "templates/core",
    "templates/accounts",
    "templates/agriculteurs",
    "templates/silos",
    "templates/marche",
    "templates/imf",
    "templates/warrantage",
    "templates/traduction",
    "templates/administration",
    "templates/notifications",
    "templates/partials",
    "templates/emails",
    "static/css",
    "static/js",
    "static/img",
    "locale/fr/LC_MESSAGES",
    "locale/en/LC_MESSAGES",
    "locale/wo/LC_MESSAGES",
    "media",
    "staticfiles",
    "tests",
]

# ─── Fichiers __init__.py nécessaires ────────────────────────────────────────
INIT_FILES = [
    "apps/__init__.py",
    "apps/core/__init__.py",
    "apps/core/management/__init__.py",
    "apps/core/management/commands/__init__.py",
    "apps/core/templatetags/__init__.py",
    "apps/accounts/__init__.py",
    "apps/silos/__init__.py",
    "apps/silos/templatetags/__init__.py",
    "apps/agriculteurs/__init__.py",
    "apps/warrantage/__init__.py",
    "apps/marche/__init__.py",
    "apps/imf/__init__.py",
    "apps/notifications/__init__.py",
    "apps/traduction/__init__.py",
    "apps/intelligence/__init__.py",
    "apps/administration/__init__.py",
    "tests/__init__.py",
]

# ─── Fichiers vides à créer (stubs) ─────────────────────────────────────────
STUB_FILES = {
    "apps/core/urls.py": "from django.urls import path\nfrom . import views\napp_name = 'core'\nurlpatterns = [path('', views.accueil, name='accueil')]\n",
    "apps/core/dashboard_urls.py": "from django.urls import path\nfrom . import views\napp_name = 'dashboard'\nurlpatterns = [path('', views.dashboard_redirect, name='redirect')]\n",
    "apps/core/views.py": """from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def accueil(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    return render(request, 'core/accueil.html')

@login_required
def dashboard_redirect(request):
    return redirect(request.user.get_dashboard_url())
""",
    "apps/core/context_processors.py": """def grenier_commun_context(request):
    context = {'app_name': 'Grenier Commun'}
    if request.user.is_authenticated:
        from apps.notifications.models import Notification
        context['notifications_non_lues'] = Notification.objects.filter(
            destinataire=request.user,
            statut__in=['EN_ATTENTE', 'ENVOYE'],
            canal='APP'
        ).count()
    return context
""",
    "apps/core/admin.py": "from django.contrib import admin\n",
    "apps/core/apps.py": """from django.apps import AppConfig
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'
""",
    "apps/accounts/admin.py": """from django.contrib import admin
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
""",
    "apps/accounts/apps.py": """from django.apps import AppConfig
class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Comptes Utilisateurs'
""",
    "apps/accounts/urls.py": """from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('profil/', views.profil, name='profil'),
    path('otp/verifier/', views.verifier_otp, name='verifier_otp'),
]
""",
    "apps/silos/apps.py": """from django.apps import AppConfig
class SilosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.silos'
    verbose_name = 'Silos & Stockage'
""",
    "apps/silos/admin.py": """from django.contrib import admin
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
""",
    "apps/silos/urls.py": """from django.urls import path
from . import views
app_name = 'silos'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('depot/nouveau/', views.nouveau_depot, name='nouveau_depot'),
    path('depot/<int:pk>/', views.detail_depot, name='detail_depot'),
    path('retrait/<int:depot_pk>/', views.enregistrer_retrait, name='enregistrer_retrait'),
    path('alertes/', views.alertes, name='alertes'),
    path('alertes/<int:pk>/acquitter/', views.acquitter_alerte, name='acquitter_alerte'),
    path('rapport/', views.rapport_mensuel, name='rapport_mensuel'),
    path('conditions/mettre-a-jour/', views.mettre_a_jour_conditions, name='maj_conditions'),
]
""",
    "apps/agriculteurs/apps.py": """from django.apps import AppConfig
class AgriculteursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.agriculteurs'
    verbose_name = 'Espace Agriculteur'
""",
    "apps/agriculteurs/urls.py": """from django.urls import path
from . import views
app_name = 'agriculteurs'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('stock/', views.mes_stocks, name='mes_stocks'),
    path('depot/<int:pk>/', views.detail_depot, name='detail_depot'),
    path('prix/', views.prix_marche, name='prix_marche'),
    path('warrantage/', views.mes_warrantages, name='mes_warrantages'),
    path('warrantage/demander/<int:depot_pk>/', views.demander_warrantage, name='demander_warrantage'),
    path('ventes/', views.mes_ventes, name='mes_ventes'),
    path('profil/', views.mon_profil, name='mon_profil'),
]
""",
    "apps/warrantage/apps.py": """from django.apps import AppConfig
class WarrantageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.warrantage'
    verbose_name = 'Warrantage & Crédit'
""",
    "apps/warrantage/urls.py": """from django.urls import path
from . import views
app_name = 'warrantage'
urlpatterns = [
    path('demande/<int:pk>/', views.detail_demande, name='detail_demande'),
]
""",
    "apps/marche/apps.py": """from django.apps import AppConfig
class MarcheConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.marche'
    verbose_name = 'Marché & Acheteurs'
""",
    "apps/marche/urls.py": """from django.urls import path
from . import views
app_name = 'marche'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('offre/nouvelle/', views.nouvelle_offre, name='nouvelle_offre'),
    path('offre/<int:pk>/', views.detail_offre, name='detail_offre'),
    path('transactions/', views.mes_transactions, name='mes_transactions'),
]
""",
    "apps/imf/apps.py": """from django.apps import AppConfig
class ImfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.imf'
    verbose_name = 'Espace IMF'
""",
    "apps/imf/urls.py": """from django.urls import path
from . import views
app_name = 'imf'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dossiers/', views.dossiers, name='dossiers'),
    path('dossier/<int:pk>/', views.detail_dossier, name='detail_dossier'),
    path('dossier/<int:pk>/decider/', views.decider_dossier, name='decider_dossier'),
]
""",
    "apps/notifications/apps.py": """from django.apps import AppConfig
class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notifications'
""",
    "apps/notifications/urls.py": """from django.urls import path
from . import views
app_name = 'notifications'
urlpatterns = [
    path('', views.liste, name='liste'),
    path('<int:pk>/lire/', views.marquer_lu, name='marquer_lu'),
]
""",
    "apps/traduction/apps.py": """from django.apps import AppConfig
class TraductionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.traduction'
    verbose_name = 'Module IA Traduction'
""",
    "apps/traduction/urls.py": """from django.urls import path
from . import views
app_name = 'traduction'
urlpatterns = [
    path('', views.traduire, name='traduire'),
    path('historique/', views.historique, name='historique'),
    path('evaluer/<int:pk>/', views.evaluer, name='evaluer'),
    path('api/traduire/', views.api_traduire, name='api_traduire'),
]
""",
    "apps/intelligence/apps.py": """from django.apps import AppConfig
class IntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.intelligence'
    verbose_name = 'IA Métier'
""",
    "apps/administration/apps.py": """from django.apps import AppConfig
class AdministrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.administration'
    verbose_name = 'Administration GC'
""",
    "apps/administration/urls.py": """from django.urls import path
from . import views
app_name = 'administration'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('silos/', views.gestion_silos, name='gestion_silos'),
    path('utilisateurs/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('warrantage/', views.gestion_warrantage, name='gestion_warrantage'),
    path('marche/', views.gestion_marche, name='gestion_marche'),
    path('finances/', views.finances, name='finances'),
    path('donnees/', views.donnees, name='donnees'),
    path('traductions/', views.traductions, name='traductions'),
]
""",
    "manage.py": """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Impossible d'importer Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
""",
    "Procfile": "web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT\nworker: celery -A config.celery worker --loglevel=info\nbeat: celery -A config.celery beat --loglevel=info\n",
    "render.yaml": """services:
  - type: web
    name: grenier-commun
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: gunicorn config.wsgi:application
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings
      - key: DEBUG
        value: false
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: grenier-commun-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: grenier-commun-redis
          type: redis
          property: connectionString

databases:
  - name: grenier-commun-db
    databaseName: grenier_commun
    user: gc_user

  - name: grenier-commun-redis
    type: redis
""",
    ".gitignore": """__pycache__/
*.py[cod]
*.egg-info/
.env
*.sqlite3
media/
staticfiles/
.venv/
venv/
node_modules/
.DS_Store
*.log
""",
    "pytest.ini": """[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
""",
}

def main():
    print("🌾 Setup Grenier Commun — Création de l'arborescence...\n")

    # Créer les dossiers
    for d in DIRS:
        os.makedirs(d, exist_ok=True)
        print(f"  📁 {d}/")

    # Créer les __init__.py
    for f in INIT_FILES:
        if not os.path.exists(f):
            open(f, 'w').close()
            print(f"  📄 {f}")

    # Créer les fichiers stubs
    for path, content in STUB_FILES.items():
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {path}")
        else:
            print(f"  ⏭️  {path} (existe déjà)")

    print("\n✅ Arborescence créée avec succès !")
    print("\n📋 Prochaines étapes :")
    print("  1. Copier .env.example vers .env et remplir les valeurs")
    print("  2. Créer la base PostgreSQL : createdb grenier_commun")
    print("  3. pip install -r requirements.txt")
    print("  4. python manage.py migrate")
    print("  5. python manage.py createsuperuser")
    print("  6. python manage.py runserver")

if __name__ == '__main__':
    main()
