"""
Django settings for the Botokhan Store project.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================================
# >>> FIX 1 — your .env file was never actually being loaded.
# You have python-dotenv in requirements.txt, but nothing in settings.py
# ever called load_dotenv(), so locally os.environ.get('SECRET_KEY') was
# only working if you'd exported it some other way. This makes .env work
# the way it's supposed to, both locally and (harmlessly) on Render.
# ======================================================================
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass
# ======================================================================

# ----------------------------------------------------------------------
# SECURITY
# ----------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-change-this-key-before-you-deploy-botokhan-store'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'mahzarat.onrender.com']

# ----------------------------------------------------------------------
# APPLICATIONS
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'botokhan.urls'

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
                'store.context_processors.store_globals',
            ],
        },
    },
]

WSGI_APPLICATION = 'botokhan.wsgi.application'

# ----------------------------------------------------------------------
# DATABASE
# ----------------------------------------------------------------------
# ======================================================================
# >>> FIX 2 (recommended, separate from the image issue) — this was still
# hardcoded to SQLite, which lives on Render's disk. Render wipes that
# disk on every deploy, so admin accounts and products can vanish too.
# This reads DATABASE_URL if it's set (e.g. on Render, once you attach a
# Postgres database) and falls back to your local SQLite file otherwise.
# Nothing changes locally until you actually set DATABASE_URL.
# ======================================================================
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}
# ======================================================================

# ----------------------------------------------------------------------
# PASSWORD VALIDATION
# ----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------------------------------------------------
# INTERNATIONALIZATION
# ----------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------------------
# STATIC FILES
# ----------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------------------------------------------------
# MEDIA FILES — THIS IS THE ACTUAL FIX FOR YOUR UPLOADED PHOTOS
# ----------------------------------------------------------------------
# ======================================================================
# >>> FIX 3 — this whole block is new. Before, MEDIA_ROOT pointed at local
# disk unconditionally, which is why uploaded photos disappeared on Render
# (ephemeral disk) and 404'd in production (media is never served when
# DEBUG=False). Setting USE_SUPABASE_STORAGE=True routes every upload
# (product photos + hero/lookbook photos) to Supabase Storage instead,
# which serves them over a permanent public URL, independent of Render.
# ======================================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # only used when USE_SUPABASE_STORAGE is False

USE_SUPABASE_STORAGE = os.environ.get('USE_SUPABASE_STORAGE', 'False') == 'True'

if USE_SUPABASE_STORAGE:
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
    SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'product-images')

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise Exception(
            'USE_SUPABASE_STORAGE is True but SUPABASE_URL / SUPABASE_SERVICE_KEY '
            'are not set. Add them in Render -> Environment (or your local .env).'
        )

    STORAGES = {
        'default': {'BACKEND': 'store.storage_backends.SupabaseStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
else:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    }
# ======================================================================
# <<< END FIX 3
# ======================================================================

# ----------------------------------------------------------------------
# AUTH / ADMIN PANEL REDIRECTS
# ----------------------------------------------------------------------
LOGIN_URL = '/admin-panel/login/'
LOGIN_REDIRECT_URL = '/admin-panel/dashboard/'
LOGOUT_REDIRECT_URL = '/admin-panel/login/'

# Currency symbol used across the storefront and admin panel.
STORE_CURRENCY_SYMBOL = '₦'
