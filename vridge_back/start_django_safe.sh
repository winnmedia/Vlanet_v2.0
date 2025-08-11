#!/bin/bash

echo "🚀 Starting Django Recovery Process"
echo "=================================="

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=config.settings.railway_minimal
export PYTHONUNBUFFERED=1
export DJANGO_LOG_LEVEL=ERROR

# 포트 설정
PORT=${PORT:-8000}
echo "Port: $PORT"

# Python 경로 확인
echo "Python version:"
python --version

# 필수 패키지 확인
echo "Checking required packages..."
python -c "import django; print(f'Django: {django.__version__}')" 2>/dev/null || echo "Django not found"
python -c "import psycopg2; print('PostgreSQL driver: OK')" 2>/dev/null || echo "PostgreSQL driver not found"

# 데이터베이스 연결 테스트 (실패해도 계속)
echo "Testing database connection..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway_minimal')
try:
    import django
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️ Database connection failed: {e}')
    print('Continuing without database...')
" 2>&1

# Django 복구 서버 실행
echo "Starting Django recovery server..."
exec python django_recovery.py