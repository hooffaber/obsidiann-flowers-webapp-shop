from pathlib import Path

from settings.apps import *  # noqa: F401, F403
from settings.auth import *  # noqa: F401, F403
from settings.caches import *  # noqa: F401, F403
from settings.celery import *  # noqa: F401, F403
from settings.cors import *  # noqa: F401, F403
from settings.databases import *  # noqa: F401, F403
from settings.environment import *  # noqa: F401, F403
from settings.logging import *  # noqa: F401, F403
from settings.rest_framework import *  # noqa: F401, F403
from settings.storage import *  # noqa: F401, F403
from settings.telegram import *  # noqa: F401, F403
from settings.tinymce import *  # noqa: F401, F403
from settings.unfold import *  # noqa: F401, F403

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'
ASGI_APPLICATION = 'asgi.application'

# Security
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
