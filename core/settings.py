"""
Ustawienia Django dla projektu core.
"""

import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab
from dotenv import load_dotenv

# Ścieżki wewnątrz projektu buduje się tak: BASE_DIR / 'podkatalog'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# UWAGA BEZPIECZEŃSTWA: klucz sekretny używany na produkcji musi pozostać tajny!
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-cf3g-7io8^q%tlbe31@oy(w-i5epudr9713$*8isr@l8nchxhc'
)

# UWAGA BEZPIECZEŃSTWA: nie uruchamiaj z debug włączonym na produkcji!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', 
    'localhost,127.0.0.1'
    ).split(',')

CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost"
).split(",")


# Definicja aplikacji

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'djoser',
    'drf_spectacular',
    'strawberry_django',
    'articles',
    'sources',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Baza danych
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'newshub'),
        'USER': os.environ.get('DB_USER', 'newshub_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'newshub_pass'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),  
    } 
}


# Walidacja haseł
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internacjonalizacja
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Pliki statyczne (CSS, JavaScript, obrazki)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    # Własny research: krótszy access token ze względów bezpieczeństwa,
    # dłuższy refresh token dla wygody użytkownika (nie trzeba się
    # logować co kilka minut)
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}


# drf-spectacular (dokumentacja API)

SPECTACULAR_SETTINGS = {
    'TITLE': 'NewsHub API',
    'DESCRIPTION': 'Agregator wiadomości - REST API do przeglądania, zgłaszania i moderacji artykułów.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Redis / cache
REDIS_URL = os.environ.get(
    "REDIS_URL",
    f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:6379"
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Celery
CELERY_BROKER_URL = f"{REDIS_URL}/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

CELERY_TASK_ROUTES = {
    "sources.tasks.*": {"queue": "rss"},
}

CELERY_TASK_DEFAULT_QUEUE = "default"

CELERY_BEAT_SCHEDULE = {
    "fetch-rss-every-30-min": {
        "task": "sources.tasks.fetch_all_active_feeds",
        "schedule": crontab(minute="*/30"),
    },
}
