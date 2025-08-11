#!/usr/bin/env python3
"""
 Django  import   
"""
import os
import sys

# Django 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.railway")

print("=== Django Import  ===\n")

#   
packages = [
    'django',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'whitenoise',
    'dj_database_url',
    'gunicorn',
]

for package in packages:
    try:
        __import__(package)
        print(f" {package}")
    except ImportError as e:
        print(f" {package}: {e}")

print("\n=== Django  import  ===\n")

# Django  
try:
    import django
    django.setup()
    print(" Django   ")
except Exception as e:
    print(f" Django   : {e}")
    sys.exit(1)

#  import 
from django.conf import settings

for app in settings.INSTALLED_APPS:
    try:
        __import__(app)
        print(f" {app}")
    except ImportError as e:
        print(f" {app}: {e}")

print("\n=== URL   ===\n")

# URL  
try:
    from django.urls import include, path
    from config.urls import urlpatterns
    print(f" URL    ({len(urlpatterns)})")
except Exception as e:
    print(f" URL   : {e}")

print("\n  !")