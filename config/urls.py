"""
Grenier Commun — URLs principales
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse

def health(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    # Healthcheck Railway
    path('health/', health),

    # Admin Django (accès restreint)
    path('gc-admin-secret/', admin.site.urls),

    # Internationalisation
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # ── Page d'accueil publique ──────────────────────────────────────────────
    path('', include('apps.core.urls', namespace='core')),

    # ── Authentification ────────────────────────────────────────────────────
    path('auth/', include('apps.accounts.urls', namespace='accounts')),
    path('auth/', include('allauth.urls')),

    # ── Dashboard (redirect selon rôle) ─────────────────────────────────────
    path('dashboard/', include('apps.core.dashboard_urls', namespace='dashboard')),

    # ── Espace Agriculteur ───────────────────────────────────────────────────
    path('agriculteur/', include('apps.agriculteurs.urls', namespace='agriculteurs')),

    # ── Espace Gestionnaire ──────────────────────────────────────────────────
    path('gestionnaire/', include('apps.silos.urls', namespace='silos')),

    # ── Espace Acheteur ──────────────────────────────────────────────────────
    path('marche/', include('apps.marche.urls', namespace='marche')),

    # ── Espace IMF ───────────────────────────────────────────────────────────
    path('imf/', include('apps.imf.urls', namespace='imf')),

    # ── Espace Admin Grenier Commun ──────────────────────────────────────────
    path('administration/', include('apps.administration.urls', namespace='administration')),

    # ── Warrantage ───────────────────────────────────────────────────────────
    path('warrantage/', include('apps.warrantage.urls', namespace='warrantage')),

    # ── Notifications ────────────────────────────────────────────────────────
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),

    # ── Module Traduction ────────────────────────────────────────────────────
    path('traduction/', include('apps.traduction.urls', namespace='traduction')),

    # ── Chatbot IA ───────────────────────────────────────────────────────────
    path('chatbot/', include('apps.chatbot.urls', namespace='chatbot')),

    prefix_default_language=True,
)

# ── Médias en développement ──────────────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
