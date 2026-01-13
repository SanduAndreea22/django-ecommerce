"""
Django settings for Cash-only eCommerce (test with real email).
"""
import os
from pathlib import Path
import dj_database_url

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------
# Security
# -------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'cheie-temporara-pt-local')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'django-ecommerce-c2s6.onrender.com',  # <--- adaugă aici
]

# -------------------------------
# Applications
# -------------------------------
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'accounts',
    'products',
    'cart',
    'orders',
    'payments',
    'coupons',
    'dashboard',
]

# -------------------------------
# Middleware
# -------------------------------
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
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------
# URLs & WSGI
# -------------------------------
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# -------------------------------
# Templates
# -------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -------------------------------
# Database (SQLite for test)
# -------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Railway / Production
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    # Local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# -------------------------------
# Password validation
# -------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------
# Internationalization
# -------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -------------------------------
# Static & Media files
# -------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # optional for collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------------------
# Authentication & Custom User
# -------------------------------
AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailBackend',  # login with email or username
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# -------------------------------
# Messages
# -------------------------------
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# -------------------------------
# Email (Real Gmail for test)
# -------------------------------
#EMAIL_HOST_USER = EMAIL_HOST_USER
#EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
# DEFAULT_FROM_EMAIL = f'CashOnly eCommerce <{EMAIL_HOST_USER}>'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"CashOnly eCommerce <{os.environ.get('EMAIL_HOST_USER')}>"
EMAIL_FAIL_SILENTLY = True
# -------------------------------
# Default primary key field type
# -------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



