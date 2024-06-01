from django.core.management.utils import get_random_secret_key
from pathlib import Path
import os
import sys
import dj_database_url
from django.conf import settings
import django_heroku
from decouple import config 


BASE_DIR = Path(__file__).resolve().parent.parent


from dotenv import load_dotenv

load_dotenv()



SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

#SECRET_KEY = 'django-insecure-)1d*4-vi8ps%h(fki%=(&uw5s4)v1l7cnxm4#b&!2-90&v1h9#'


DEBUG = os.getenv("DEBUG", "False") == "True"
#DEBUG = True

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,mwalimufocus.co.ke,mwalimufocus.com,localhost,mwalimufocus-ec482d83d7a7.herokuapp.com").split(",") + ['testserver', 'www.testserver']



INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.redirects',
    'shop',
    'vendors',
    'accounts',
    'storages',
    'pages',
    'tinymce',
    'compressor',
]

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

WSGI_APPLICATION = 'eduresources.wsgi.application'



DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"
#DEVELOPMENT_MODE = True



if DEVELOPMENT_MODE is True:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
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
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


COMPRESS_ENABLED = True

COMPRESS_OFFLINE = True



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CSRF_TRUSTED_ORIGINS = [
    'https://mwalimufocus.co.ke',
    'https://mwalimufocus.com',
    'https://mwalimufocus-ec482d83d7a7.herokuapp.com'
]





AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
AWS_LOCATION = os.getenv('AWS_LOCATION')
AWS_DEFAULT_ACL = os.getenv('AWS_DEFAULT_ACL')
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_QUERYSTRING_AUTH = os.getenv('AWS_QUERYSTRING_AUTH')
AWS_S3_VERIFY_SSL = os.getenv('AWS_S3_VERIFY_SSL') == 'True'


INTASEND_TOKEN = os.getenv("INTASEND_TOKEN")
INTASEND_PUBLISHABLE_KEY = os.getenv("INTASEND_PUBLISHABLE_KEY")




EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.privateemail.com'
EMAIL_PORT = 587  
EMAIL_USE_TLS = True  
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') 
DEFAULT_FROM_EMAIL = 'Mwalimu Focus <info@mwalimufocus.com>'


SITE_ID = 1


django_heroku.settings(locals())