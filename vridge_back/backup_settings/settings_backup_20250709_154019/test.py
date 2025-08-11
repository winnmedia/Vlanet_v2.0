"""
  Django  - Railway 
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

#  
SECRET_KEY = 'django-insecure-test-key-for-railway'
DEBUG = True
ALLOWED_HOSTS = ['*']

#  
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
]

#  
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls_ultra_simple'

#  - PostgreSQL 
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///' + str(BASE_DIR / 'db.sqlite3')),
        conn_max_age=600,
    )
}

# 
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_TZ = True