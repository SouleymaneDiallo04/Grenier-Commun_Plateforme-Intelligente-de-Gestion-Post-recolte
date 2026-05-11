"""
Grenier Commun — Settings
Architecture : Interface / Logique Métier / Données / IA
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url

# ─── CHEMINS ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── SÉCURITÉ ─────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# ─── APPLICATIONS ─────────────────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    # Auth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # REST
    'rest_framework',
    'rest_framework_simplejwt',
    # Frontend
    'django_htmx',
    'widget_tweaks',
    'crispy_forms',
    'crispy_tailwind',
    # Filtres
    'django_filters',
    # Sécurité
    'axes',
    # Téléphone
    'phonenumber_field',
    # Cloudinary
    'cloudinary',
    'cloudinary_storage',
]

LOCAL_APPS = [
    # Cœur
    'apps.core',
    # Utilisateurs & Auth
    'apps.accounts',
    # Silos & Stockage
    'apps.silos',
    # Agriculteurs
    'apps.agriculteurs',
    # Warrantage / Crédit
    'apps.warrantage',
    # Marché / Acheteurs
    'apps.marche',
    # IMF Partenaires
    'apps.imf',
    # Notifications
    'apps.notifications',
    # Module IA Traduction
    'apps.traduction',
    # Module IA Métier
    'apps.intelligence',
    # Administration GC
    'apps.administration',
    # Chatbot IA
    'apps.chatbot',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── MIDDLEWARE ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'axes.middleware.AxesMiddleware',
    'apps.core.middleware.AutoTranslateMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ─── TEMPLATES ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                # Contexte global Grenier Commun
                'apps.core.context_processors.grenier_commun_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ─── BASE DE DONNÉES ──────────────────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ─── CACHE & SESSIONS ─────────────────────────────────────────────────────────
REDIS_URL = config('REDIS_URL', default='redis://127.0.0.1:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 3600,  # 1 heure par défaut
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24h
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True

# ─── AUTHENTIFICATION ─────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── ALLAUTH ──────────────────────────────────────────────────────────────────
SITE_ID = 1
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/auth/connexion/'

# ─── INTERNATIONALISATION ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'fr'
LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('wo', 'Wolof'),
    ('ar', 'العربية'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'Africa/Dakar'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ─── FICHIERS STATIQUES ───────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── MÉDIAS (Cloudinary en prod, local en dev) ────────────────────────────────
if DEBUG:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME', default=''),
        'API_KEY': config('CLOUDINARY_API_KEY', default=''),
        'API_SECRET': config('CLOUDINARY_API_SECRET', default=''),
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── EMAIL ────────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default=f"Grenier Commun <{config('EMAIL_HOST_USER', default='noreply@greniercommun.sn')}>",
)

# ─── CELERY ───────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    # Mise à jour des prix de marché chaque lundi matin
    'update-prix-marche': {
        'task': 'apps.marche.tasks.update_prix_marche',
        'schedule': 604800,  # 7 jours
    },
    # Calcul des recommandations de vente chaque lundi
    'generer-recommandations': {
        'task': 'apps.intelligence.tasks.generer_recommandations_vente',
        'schedule': 604800,
    },
    # Vérification des alertes silos toutes les heures
    'verifier-alertes-silos': {
        'task': 'apps.silos.tasks.verifier_conditions_silos',
        'schedule': 3600,
    },
    # Facturation mensuelle du stockage
    'facturation-stockage': {
        'task': 'apps.warrantage.tasks.calculer_loyers_stockage',
        'schedule': 2592000,  # 30 jours
    },
}

# ─── REST FRAMEWORK ───────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# ─── DJANGO-AXES (protection brute force) ────────────────────────────────────
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # heure
AXES_LOCKOUT_TEMPLATE = 'auth/compte_bloque.html'
AXES_RESET_ON_SUCCESS = True
# axes 6.x + Django 5 : session_hash NOT NULL avant que la session soit créée
AXES_DISABLE_ACCESS_LOG = True

# ─── CRISPY FORMS ─────────────────────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = 'tailwind'
CRISPY_TEMPLATE_PACK = 'tailwind'

# ─── TÉLÉPHONE ────────────────────────────────────────────────────────────────
PHONENUMBER_DEFAULT_REGION = 'SN'  # Sénégal par défaut

# ─── SMS (TWILIO) ─────────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# ─── IA CHATBOT ───────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
MISTRAL_API_KEY = config('MISTRAL_API_KEY', default='')

# ─── TRADUCTION IA ────────────────────────────────────────────────────────────
HUGGINGFACE_API_KEY = config('HUGGINGFACE_API_KEY', default='')
GOOGLE_TRANSLATE_API_KEY = config('GOOGLE_TRANSLATE_API_KEY', default='')
NLLB_MODEL_NAME = 'facebook/nllb-200-distilled-600M'
TRANSLATION_CACHE_TIMEOUT = 86400  # 24h
SUPPORTED_LANGUAGES = {
    'fr': {'nom': 'Français',  'nllb_code': 'fra_Latn', 'flag': '🇫🇷'},
    'en': {'nom': 'English',   'nllb_code': 'eng_Latn', 'flag': '🇬🇧'},
    'wo': {'nom': 'Wolof',     'nllb_code': 'wol_Latn', 'flag': '🇸🇳'},
    'ar': {'nom': 'العربية',   'nllb_code': 'arb_Arab', 'flag': '🇸🇦'},
}

# ─── SÉCURITÉ EN PRODUCTION ───────────────────────────────────────────────────
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ─── LOGGING ──────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'apps': {'handlers': ['console'], 'level': 'DEBUG' if DEBUG else 'INFO', 'propagate': False},
    },
}

# ─── CONSTANTES MÉTIER GRENIER COMMUN ────────────────────────────────────────
GC_TAUX_LOCATION_MENSUEL = 0.015       # 1.5% de la valeur du stock par mois
GC_TAUX_WARRANTAGE = 0.70              # 70% de la valeur du stock empruntable
GC_COMMISSION_VENTE = 0.02            # 2% sur chaque transaction de vente
GC_COMMISSION_WARRANTAGE = 0.015       # 1.5% sur chaque crédit accordé
GC_DUREE_MAX_STOCKAGE_JOURS = 180     # 6 mois maximum de stockage
GC_SMS_LANGUE_DEFAUT = 'fr'
