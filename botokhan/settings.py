"""
Django settings for the Botokhan Store project.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------------
# SECURITY
# ----------------------------------------------------------------------
# Replace this with your own secret key before deploying (never reuse this one).
#SECRET_KEY = 'django-insecure-change-this-key-before-you-deploy-botokhan-store'


# The second argument acts as a backup for local development
SECRET_KEY = os.environ.get('SECRET_KEY')


# Turn this off in production.
DEBUG = False

#ALLOWED_HOSTS = ['']  # Tighten this to your real domain(s) before deploying.

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
# SQLite by default — zero setup, perfect for development or a small store.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# To use MySQL instead, install `mysqlclient` (pip install mysqlclient) and
# replace the DATABASES block above with:
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'botokhan_store',
#         'USER': 'root',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {'charset': 'utf8mb4'},
#     }
# }

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
# STATIC & MEDIA FILES
# ----------------------------------------------------------------------
#STATIC_URL = 'static/'
#STATIC_ROOT = BASE_DIR / 'staticfiles'  # used by `collectstatic` in production
# No STATICFILES_DIRS needed — Django's AppDirectoriesFinder automatically
# picks up store/static/ since 'store' is in INSTALLED_APPS.


STATIC_URL = "/static/"

# The absolute path to the directory where collectstatic will collect static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles") 

# Optional: Turn on WhiteNoise storage compression and caching support
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"





MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # uploaded product/site photos live here

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------------------------------------------------------
# AUTH / ADMIN PANEL REDIRECTS
# ----------------------------------------------------------------------
LOGIN_URL = '/admin-panel/login/'
LOGIN_REDIRECT_URL = '/admin-panel/dashboard/'
LOGOUT_REDIRECT_URL = '/admin-panel/login/'

# Currency symbol used across the storefront and admin panel.
STORE_CURRENCY_SYMBOL = '₦'
