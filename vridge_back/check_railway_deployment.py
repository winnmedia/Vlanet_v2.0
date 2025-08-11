#!/usr/bin/env python
"""
Railway   
  Railway     .
"""
import os
import sys
import django

# Django  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings'))
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from django.db import connection

print("=" * 80)
print("VideoPlanet Railway   ")
print("=" * 80)

# 1. Django   
print("\n1. Django  :")
print(f"   - DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set')}")
print(f"   -   : {settings.SETTINGS_MODULE}")

# 2.   
print("\n2.  :")
print(f"   - EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"   - EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"   - EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"   - EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"   - EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"   - EMAIL_HOST_PASSWORD: {'' if settings.EMAIL_HOST_PASSWORD else ' '}")
if settings.EMAIL_HOST_PASSWORD:
    print(f"   - API Key : {settings.EMAIL_HOST_PASSWORD[:10]}...")
print(f"   - DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# SendGrid   
sendgrid_key = os.environ.get('SENDGRID_API_KEY', '')
print(f"\n   SendGrid :")
print(f"   - SENDGRID_API_KEY: {'' if sendgrid_key else ' '}")
if sendgrid_key:
    print(f"   - API Key : {sendgrid_key[:10]}...")

# 3. CORS  
print("\n3. CORS :")
print(f"   - CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', 'Not set')}")
print(f"   - CORS_ALLOW_CREDENTIALS: {getattr(settings, 'CORS_ALLOW_CREDENTIALS', 'Not set')}")
cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
print(f"   - CORS_ALLOWED_ORIGINS: ({len(cors_origins)} )")
for origin in cors_origins[:5]:  #  5 
    print(f"      - {origin}")
if len(cors_origins) > 5:
    print(f"      ...   {len(cors_origins) - 5}")

# 4.   
print("\n4.  :")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("   - PostgreSQL :  ")
        cursor.execute("SELECT COUNT(*) FROM django_migrations")
        migration_count = cursor.fetchone()[0]
        print(f"   -  : {migration_count}")
except Exception as e:
    print(f"   - PostgreSQL :   ({str(e)})")

# 5.    
print("\n5.   :")
print(f"   - MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   - MEDIA_URL: {settings.MEDIA_URL}")
media_exists = os.path.exists(settings.MEDIA_ROOT)
print(f"   -   : {'' if media_exists else ''}")

# 6.    
print("\n6.   :")
print(f"   - STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"   - STATIC_URL: {settings.STATIC_URL}")
static_exists = os.path.exists(settings.STATIC_ROOT)
print(f"   -    : {'' if static_exists else ''}")

# 7.   
print("\n7.  :")
print(f"   - DEBUG: {settings.DEBUG}")
print(f"   - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}...")
print(f"   - SECURE_SSL_REDIRECT: {getattr(settings, 'SECURE_SSL_REDIRECT', 'Not set')}")
print(f"   - SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'Not set')}")
print(f"   - CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set')}")

# 8.   
print("\n8. Railway  :")
railway_env_vars = ['RAILWAY_ENVIRONMENT', 'PORT', 'DATABASE_URL']
for var in railway_env_vars:
    value = os.environ.get(var, 'Not set')
    if var == 'DATABASE_URL' and value != 'Not set':
        print(f"   - {var}:  (  )")
    else:
        print(f"   - {var}: {value}")

# 9.    ()
print("\n9.   :")
if '--test-email' in sys.argv:
    test_email = sys.argv[sys.argv.index('--test-email') + 1]
    try:
        send_mail(
            '[VideoPlanet] Railway  ',
            '  Railway     .',
            settings.DEFAULT_FROM_EMAIL,
            [test_email],
            fail_silently=False,
        )
        print(f"   -   :   ({test_email})")
    except Exception as e:
        print(f"   -   :  ")
        print(f"     : {str(e)}")
else:
    print("   -  --test-email []  ")

print("\n" + "=" * 80)
print(" ")
print("=" * 80)