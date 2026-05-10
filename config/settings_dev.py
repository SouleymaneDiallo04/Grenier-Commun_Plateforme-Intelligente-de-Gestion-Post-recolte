"""
settings_dev.py — Paramètres pour le développement local
- SQLite à la place de PostgreSQL (pas de service requis)
- Cache mémoire à la place de Redis (pas de service requis)
- Sessions en base de données
- Email vers la console
"""
from .settings import *

# ─── BASE DE DONNÉES — SQLite ─────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── CACHE — Mémoire locale (pas de Redis) ────────────────────────────────────
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'grenier-commun-dev',
    }
}

# ─── SESSIONS — Base de données (pas de Redis) ───────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# ─── EMAIL — Console (pas d'envoi réel) ──────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ─── FICHIERS STATIQUES — Mode dev simple ────────────────────────────────────
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ─── APPS — Retirer les apps non installées en dev ───────────────────────────
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in (
    'cloudinary',
    'cloudinary_storage',
)]
INSTALLED_APPS += ['debug_toolbar']

# ─── DEBUG TOOLBAR ───────────────────────────────────────────────────────────
MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']
