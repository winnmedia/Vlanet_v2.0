#!/usr/bin/env python
"""
Minimal Django server test for Railway debugging
"""
import os
import sys

# Django settings 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

# Django 초기화
import django
django.setup()

# 기본 import 테스트
try:
    from django.core.wsgi import get_wsgi_application
    print("✅ Django WSGI import successful")
except ImportError as e:
    print(f"❌ Django WSGI import failed: {e}")
    sys.exit(1)

# Settings 테스트
try:
    from django.conf import settings
    print(f"✅ Settings loaded: DEBUG={settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}...")
except Exception as e:
    print(f"❌ Settings error: {e}")
    sys.exit(1)

# Database 연결 테스트
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
except Exception as e:
    print(f"⚠️ Database connection failed (this might be expected): {e}")

# URL 설정 테스트
try:
    from config import urls
    print(f"✅ URL configuration loaded, {len(urls.urlpatterns)} patterns")
except Exception as e:
    print(f"❌ URL configuration error: {e}")
    sys.exit(1)

# WSGI application 테스트
try:
    application = get_wsgi_application()
    print("✅ WSGI application created successfully")
except Exception as e:
    print(f"❌ WSGI application creation failed: {e}")
    sys.exit(1)

print("\n🎉 All basic tests passed! Server should be able to start.")