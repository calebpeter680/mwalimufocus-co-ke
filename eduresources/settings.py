from django.core.management.utils import get_random_secret_key
from pathlib import Path
import os
import sys
import dj_database_url
from django.conf import settings
import django_heroku
from decouple import config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret Key and Debug
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())


DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,63a9-102-6-193-121.ngrok-free.app,mwalimufocus.co.ke,mwalimufocus.com,localhost,mwalimufocus-ec482d83d7a7.herokuapp.com").split(",") + ['testserver', 'www.testserver']

# Installed Apps
INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'daphne',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.redirects',
    'shop',
    'vendors',
    'accounts',
    'storages',
    'pages',
    'examgenerator',
    'tinymce',
]

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'shop.middleware.DomainRedirectMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    
]

ROOT_URLCONF = 'eduresources.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



ASGI_APPLICATION = 'eduresources.asgi.application'


DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"

if DEVELOPMENT_MODE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL),
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.CustomUser'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True
WHITENOISE_GZIP = True
WHITENOISE_BROTLI = True
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    'https://mwalimufocus.co.ke',
    'https://mwalimufocus.com',
    'https://mwalimufocus-ec482d83d7a7.herokuapp.com',
    'https://63a9-102-6-193-121.ngrok-free.app'
]




AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_LOCATION = os.getenv('AWS_LOCATION')
AWS_DEFAULT_ACL = os.getenv('AWS_DEFAULT_ACL')
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_QUERYSTRING_AUTH = os.getenv('AWS_QUERYSTRING_AUTH') == 'True'
AWS_S3_VERIFY_SSL = os.getenv('AWS_S3_VERIFY_SSL') == 'True'




INTASEND_TOKEN = os.getenv("INTASEND_TOKEN")
INTASEND_PUBLISHABLE_KEY = os.getenv("INTASEND_PUBLISHABLE_KEY")


MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'sm1.cloudoon.com'
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'Mwalimu Focus <info@mwalimufocus.com>'


SITE_ID = 1


django_heroku.settings(locals())

SCHEDULER_AUTOSTART = True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "daphne": {  # Daphne logs
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}



