from corsheaders.defaults import default_headers
from datetime import timedelta
from pathlib import Path
import os
from .jazzmin_settings import *
from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", default="foo")

DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "parler",
    "drf_yasg",
    "corsheaders",
    "django_summernote",
    "sorl.thumbnail",
    "paycomuz",
    "clickuz",
    "rosetta",
   
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dacha.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "dacha.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE"),
        "NAME": os.environ.get("SQL_DATABASE"),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "api.User"

LANGUAGE_CODE = "uz"
LANGUAGES = (
    ("uz", _("Uzbek")),
    ("ru", _("Russian")),
    ("en", _("English")),
)
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_L10N = True
USE_TZ = False

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGS = ["en", "uz", "ru"]

PARLER_LANGUAGES = {
    None: tuple([{"code": lang} for lang in LANGS]),
    "default": {
        "fallbacks": ["uz"],
        "hide_untranslated": False,
    }
}

SMS_EXPIRE_SECONDS = 120

REDIS_HOST = "localhost"
REDIS_PORT = 6379

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=29, hours=23)
}

# CORS_ALLOWED_ORIGINS = [
#     "localhost:3000",
#     "http://localhost:3000",
#     "https://dachaturizm.netlify.app/",
#     "http://dachaturizm.netlify.app/",
#     "dachaturizm.netlify.app/"
# ]

CORS_ALLOW_ALL_ORIGINS = True

SMS_AUTH_TOKEN = os.environ.get("SMS_AUTH_TOKEN")

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

CELERY_TIMEZONE = "Asia/Tashkent"

SERVER_IP = os.environ.get("SERVER_IP")

PAYCOM_SETTINGS = {
    "KASSA_ID": "619f66f3bede17c4c1b71a8f",
    "TOKEN": "619f66f3bede17c4c1b71a8f",
    "SECRET_KEY": "tWxo5GCP1tAPnN#Q&7mWUDHqRQjAGusajej9",
    "ACCOUNTS": {
        "KEY": "order_id"
    }
}


CLICK_SETTINGS = {
    "service_id": "19845",
    "merchant_id": "14353",
    "secret_key": "DjyJdIAOFmAA",
    "merchant_user_id": "22891"
}

USD_TO_UZS = 10700

OTP_HASH_CODE = os.environ.get("OTP_HASH_CODE")

LOGIN_REDIRECT_URL = "/ru/admin/login/"
LOGIN_URL = "/ru/admin/login/"

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

FCM_SERVICE_TOKEN = os.environ.get("FCM_SERVICE_TOKEN")

CORS_ALLOW_HEADERS = list(default_headers) + [
    "From-mobile",
]
